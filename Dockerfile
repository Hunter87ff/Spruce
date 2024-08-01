FROM python:3.10-slim
WORKDIR /app
COPY . .
# COPY requirements.txt requirements.txt
RUN pip install -r src/requirements.txt
EXPOSE 8787
RUN python src/runner.py