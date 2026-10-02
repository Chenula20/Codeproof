"""Real Google SDK serialization against synthetic HTTP transport, never live."""
import asyncio,json
import httpx,pytest
from pydantic import BaseModel,Field
from google import genai
from google.genai import types
from ai.providers import GeminiProvider,AIProviderConfig
import ai.providers.gemini as module
ACTUAL_CLIENT = genai.Client

class Answer(BaseModel):
    score:float=Field(ge=0,le=1)

def exercise(monkeypatch,handler,operation):
    actual=ACTUAL_CLIENT;calls=[];transports=[]
    def factory(**kwargs):
        options=kwargs['http_options'];calls.append((kwargs['api_key'],options))
        options.async_client_args={'transport':httpx.MockTransport(handler),'trust_env':False}
        options.client_args={'transport':httpx.MockTransport(handler),'trust_env':False}
        client=actual(**kwargs)
        transports.append(client._api_client._async_httpx_client)
        return client
    monkeypatch.setattr(module.genai,'Client',factory)
    async def run():
        provider=GeminiProvider(AIProviderConfig(api_key='synthetic-gemini-key',model='fixture-model',timeout=2,temperature=.3,max_tokens=55))
        try: return await operation(provider)
        finally: await provider.close()
    result=asyncio.run(run())
    assert calls[0][0]=='synthetic-gemini-key'
    assert calls[0][1].timeout==2000 and calls[0][1].retry_options.attempts==1
    assert transports[0].is_closed
    return result

def reply(text):return httpx.Response(200,json={'candidates':[{'content':{'role':'model','parts':[{'text':text}]},'finishReason':'STOP'}]})

def test_generate_settings_and_system_instruction(monkeypatch):
    requests=[]
    def handler(request):
        requests.append(request);return reply('fixture answer')
    assert exercise(monkeypatch,handler,lambda p:p.generate('safe prompt','system instruction'))=='fixture answer'
    r=requests[0];body=json.loads(r.content)
    assert 'fixture-model:generateContent' in str(r.url)
    assert r.headers['x-goog-api-key']=='synthetic-gemini-key'
    assert body['generationConfig']['temperature']==.3 and body['generationConfig']['maxOutputTokens']==55
    assert body['systemInstruction']['parts'][0]['text']=='system instruction'
    assert len(requests)==1

def test_structured_round_trip_and_schema(monkeypatch):
    def handler(request):
        body=json.loads(request.content)
        assert body['generationConfig']['responseMimeType']=='application/json'
        assert 'score' in body['generationConfig']['responseJsonSchema']['properties']
        return reply('{"score":0.8}')
    assert exercise(monkeypatch,handler,lambda p:p.generate_structured('safe',Answer)).score==.8

@pytest.mark.parametrize('failure',['auth','missing-model','busy','unavailable','timeout','malformed','invalid','empty'])
def test_failures_hide_payload_and_do_not_retry(monkeypatch,failure):
    requests=[]
    def handler(request):
        requests.append(request)
        if failure=='timeout':raise httpx.ReadTimeout('private synthetic body',request=request)
        if failure in ('auth','missing-model','busy','unavailable'):
            return httpx.Response({'auth':401,'missing-model':404,'busy':429,'unavailable':503}[failure],json={'error':{'message':'private synthetic body','code':401,'status':'DENIED'}})
        return reply({'malformed':'not JSON private synthetic body','invalid':'{"score":9}','empty':''}[failure])
    with pytest.raises(RuntimeError) as error:exercise(monkeypatch,handler,lambda p:p.generate_structured('safe',Answer))
    assert 'private synthetic body' not in str(error.value) and 'synthetic-gemini-key' not in str(error.value)
    assert len(requests)==1

def test_embedding_order_cardinality_and_empty(monkeypatch):
    calls=[]
    def handler(request):
        calls.append(request)
        assert 'gemini-embedding-001:batchEmbedContents' in str(request.url)
        return httpx.Response(200,json={'embeddings':[{'values':[1.0,2.0]},{'values':[3.0,4.0]}]})
    assert exercise(monkeypatch,handler,lambda p:p.embed(['first','second']))==[[1.,2.],[3.,4.]]
    assert len(calls)==1
    assert exercise(monkeypatch,handler,lambda p:p.embed([]))==[]

def test_embedding_malformed_count_fails_closed(monkeypatch):
    with pytest.raises(RuntimeError):
        exercise(monkeypatch,lambda r:httpx.Response(200,json={'embeddings':[]}),lambda p:p.embed(['safe']))
