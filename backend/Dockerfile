FROM python:3.12

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./

# Install dependencies into .venv
RUN uv sync --frozen --no-install-project

COPY . ./

ENV MODE=cloud

# In a containerized environment, it's crucial that logs are written directly to stdout and stderr so Cloud Logging can capture them in real-time. Python's output is buffered by default, which can delay or cause the loss of log entries if an instance crashes.
ENV PYTHONUNBUFFERED=1

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--loop", "uvloop", "--workers", "1"]