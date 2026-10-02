import { useCallback, useEffect, useState } from 'react'
import { api } from './api.js'
import Welcome from './components/Welcome.jsx'
import { Analysis, SkillMap, Code, Investigation, Patch } from './components/Views.jsx'
import { Explorer, Coach, Bottom, Modal } from './components/Panels.jsx'

const FRESH = { challenge: null, hints: [], verdict: null, unlocked: false, proposal: null, applied: false, validation: null, readiness: null, validating: false, busy: false }
const DEFAULT_FILE = 'src/auth/handler.py'

export default function App() {
  const [screen, setScreen] = useState('welcome')
  const [tab, setTab] = useState('analysis')
  const [bTab, setBTab] = useState('problems')
  const [ov, setOv] = useState(null)
  const [skills, setSkills] = useState([])
  const [source, setSource] = useState('original')
  const [nodes, setNodes] = useState([])
  const [path, setPath] = useState(DEFAULT_FILE)
  const [file, setFile] = useState(null)
  const [modal, setModal] = useState(false)
  const [error, setError] = useState(null)
  const [s, setS] = useState(FRESH)
  const patch = (p) => setS((x) => ({ ...x, ...p }))
  const fail = (e) => { setError(e.message); setTimeout(() => setError(null), 6000) }

  useEffect(() => { Promise.all([api.overview(), api.skillMap()]).then(([o, m]) => { setOv(o); setSkills(m.skills) }).catch(fail) }, [])
  useEffect(() => { api.files(source).then((t) => setNodes(t.nodes)).catch(fail) }, [source, s.applied])
  useEffect(() => { api.file(path, source).then(setFile).catch(() => setFile(null)) }, [path, source, s.applied])

  const openFile = (p) => { setPath(p); setTab('code') }
  const startChallenge = async () => {
    patch({ busy: true })
    try { const c = await api.startChallenge(); setS({ ...FRESH, challenge: c }); setSource('challenge'); setPath('src/frontend/login.js'); setModal(false); setTab('investigation') }
    catch (e) { patch({ busy: false }); fail(e) }
  }
  const actions = {
    showSkills: () => setTab('skills'),
    hint: async () => { try { const h = await api.hint(s.hints.length + 1); setS((x) => ({ ...x, hints: [...x.hints.filter((y) => y.level !== h.level), h] })) } catch (e) { fail(e) } },
    explain: async (t) => { patch({ busy: true }); try { const v = await api.explanation(t); patch({ verdict: v, unlocked: v.patch_unlocked }) } catch (e) { fail(e) } finally { patch({ busy: false }) } },
    reviewPatch: async () => { try { patch({ proposal: s.proposal || await api.patch() }); setTab('patch') } catch (e) { fail(e) } },
  }
  const apply = async () => { try { await api.applyPatch(); patch({ applied: true }) } catch (e) { fail(e) } }
  const validate = useCallback(async () => {
    patch({ validating: true }); setBTab('sandbox')
    try { const [v] = await Promise.all([api.validate(), new Promise((r) => setTimeout(r, 1500))]); const r = await api.readiness(); patch({ validation: v, readiness: r }); setBTab('tests') }
    catch (e) { fail(e) } finally { patch({ validating: false }) }
  }, [])
  const reset = async () => { try { await api.reset() } catch (e) { fail(e) } setS(FRESH); setSource('original'); setPath(DEFAULT_FILE); setTab('analysis'); setBTab('problems') }

  const mod = s.applied
  return (
    <div className="shell">
      <div className="hdr"><div className="logo" /><b>CodeProof</b>
        {screen === 'app' && (<><span className="sub">{ov?.name}</span><span className="pill">DEMO · MOCK SERVICES</span><span className="pill green">Original Project: PROTECTED</span>
          {s.challenge ? <span className="pill purple">Challenge Copy: {mod ? 'TEMPORARILY MODIFIED' : 'TEMPORARY'}</span> : <span className="pill cyan">Analysis complete</span>}</>)}</div>
      {screen === 'welcome' ? <Welcome name={ov?.name} loading={!ov} onOpen={() => setScreen('app')} /> : (<>
        <div className="tabs">
          {[['analysis', 'Analysis'], ['skills', 'Skill Map'], ['code', 'Code'], ['investigation', 'Investigation', !s.challenge], ['patch', 'Patch Review', !s.proposal]].map(([k, l, lock]) => (
            <button key={k} className={`tab${tab === k ? ' on' : ''}`} disabled={lock} onClick={() => setTab(k)}>{l}{lock && ' 🔒'}</button>))}
          <div className="sp" /><button className="link" onClick={reset}>Reset Demo</button>
          <button className="btn go" disabled={!!s.challenge} onClick={() => setModal(true)}>Break My App</button></div>
        <div className="body">
          {s.validating && <div className="prog" />}
          {error && <div className="err">{error}</div>}
          <Explorer nodes={nodes} selected={path} onSelect={openFile} />
          <div className="col">
            {tab === 'analysis' && <Analysis ov={ov} />}
            {tab === 'skills' && <SkillMap skills={skills} />}
            {tab === 'code' && <Code file={file} source={source} />}
            {tab === 'investigation' && s.challenge && <Investigation c={s.challenge} onOpenFile={openFile} />}
            {tab === 'patch' && s.proposal && <Patch p={s.proposal} applied={s.applied} onApply={apply} onValidate={validate} validating={s.validating} validated={!!s.validation} />}
          </div>
          <Coach s={s} ov={ov} actions={actions} />
        </div>
        <Bottom s={s} ov={ov} tab={bTab} setTab={setBTab} actions={actions} />
      </>)}
      <div className="status" style={{ gridRow: 5 }}>● Guardian active · read-only<span className="sp" /><span className="r">{source === 'challenge' ? 'Challenge copy' : 'Original project'}   UTF-8</span></div>
      {modal && <Modal onCancel={() => setModal(false)} onStart={startChallenge} busy={s.busy} />}
    </div>
  )
}
