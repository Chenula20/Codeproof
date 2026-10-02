"""Start the authenticated desktop service on loopback only."""
import errno
import os
import secrets
import socket
import uvicorn
from backend.config import backend_port, load_local_environment


def bound_listener(port):
    listener=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        if hasattr(socket,'SO_EXCLUSIVEADDRUSE'):
            listener.setsockopt(socket.SOL_SOCKET,socket.SO_EXCLUSIVEADDRUSE,1)
        listener.bind(('127.0.0.1',port))
        listener.listen(128)
        return listener
    except OSError as error:
        listener.close()
        if error.errno==errno.EADDRINUSE or getattr(error,'winerror',None)==10048:
            raise SystemExit(f'CodeProof port {port} is already in use. Choose a free BACKEND_PORT and restart; leave the existing listener running.') from None
        raise SystemExit('Cannot bind the CodeProof loopback service. Check port availability and local permissions, then choose a free BACKEND_PORT.') from None


def _serve(listener,port):
    server=uvicorn.Server(uvicorn.Config('backend.main:app',host='127.0.0.1',port=port))
    server.run(sockets=[listener])


def main() -> None:
    load_local_environment()
    port=backend_port()
    token=os.getenv('CODEPROOF_TOKEN')
    if token and len(token)<32:
        raise SystemExit('CODEPROOF_TOKEN must have at least 32 characters.')
    # Reserve the exact listener before printing a generated token. Passing it
    # directly to Uvicorn prevents a check-then-bind race with another service.
    with bound_listener(port) as listener:
        if not token:
            os.environ['CODEPROOF_TOKEN']=secrets.token_urlsafe(32)
            print('Local pairing token: '+os.environ['CODEPROOF_TOKEN'],flush=True)
        _serve(listener,port)


if __name__=='__main__':
    main()
