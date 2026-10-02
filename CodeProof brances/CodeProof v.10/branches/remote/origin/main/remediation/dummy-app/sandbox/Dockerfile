FROM codeproof/sandbox:latest
# Explicit, repository-owned provisioning; never build an opened target Dockerfile.
USER 0
COPY requirements.txt /opt/codeproof-dummy-requirements.txt
RUN python -m pip install --no-cache-dir -r /opt/codeproof-dummy-requirements.txt && python -m pip check
USER 65532:65532
WORKDIR /tmp
