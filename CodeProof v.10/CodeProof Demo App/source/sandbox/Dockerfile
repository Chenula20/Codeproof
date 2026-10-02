FROM python:3.12-slim

# Trusted image setup only. Never install dependencies from an opened project.
RUN apt-get update && apt-get install -y --no-install-recommends nodejs && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /opt/codeproof-requirements.txt
RUN pip install --no-cache-dir -r /opt/codeproof-requirements.txt
USER 65532:65532
WORKDIR /tmp
ENV PYTHONDONTWRITEBYTECODE=1
CMD ["python", "-m", "pytest", "-q", "-p", "no:cacheprovider"]
