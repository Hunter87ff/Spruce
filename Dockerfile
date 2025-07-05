FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DOCKER_ENV=1 

WORKDIR /app

COPY pyproject.toml ./
COPY uv.lock ./
COPY src/ ./
COPY LICENSE ./
COPY README.md ./
COPY lava/ ./lava/

# sanitize if any .env file exists
RUN rm -f .env


RUN pip install --no-cache-dir -U uv pip

CMD ["uv", "run", "main.py"]

# Build the Docker image with the command:
# docker build -t spruce:latest .

# Run the Docker container with the command:
# docker run --rm -it spruce:latest