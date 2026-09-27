FROM python:3.11-slim

RUN groupadd -r sandbox && useradd -r -g sandbox sandbox

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chown -R sandbox:sandbox /app
USER sandbox

CMD ["python", "-m", "pytest", "tests/", "-v", "--tb=short"]
