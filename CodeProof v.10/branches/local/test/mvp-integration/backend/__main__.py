"""Start the authenticated desktop service on loopback only."""
import os
import secrets
import uvicorn


if __name__ == '__main__':
    if not os.getenv('CODEPROOF_TOKEN'):
        os.environ['CODEPROOF_TOKEN'] = secrets.token_urlsafe(32)
        print('Local pairing token: ' + os.environ['CODEPROOF_TOKEN'], flush=True)
    if len(os.environ['CODEPROOF_TOKEN']) < 32:
        raise SystemExit('CODEPROOF_TOKEN must have at least 32 characters')
    uvicorn.run('backend.main:app', host='127.0.0.1', port=int(os.getenv('BACKEND_PORT', '8000')))
