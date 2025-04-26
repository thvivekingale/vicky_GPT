# Build stage
FROM python:3.12-slim AS builder

WORKDIR /app

# Install poetry
RUN pip install poetry
RUN poetry self add poetry-plugin-export

# Copy poetry files
COPY pyproject.toml poetry.lock* ./

# Copy application code
COPY . .

# Export dependencies to requirements.txt
RUN poetry export -f requirements.txt --output requirements.txt 

# Final stage
FROM python:3.12-slim

RUN apt-get update && apt-get install -y libcairo2 python3-dev libffi-dev

WORKDIR /app

# Copy files from builder
COPY --from=builder /app/ .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Compile bytecode to improve startup latency
# -q: Quiet mode 
# -b: Write legacy bytecode files (.pyc) alongside source
# -f: Force rebuild even if timestamps are up-to-date
RUN python -m compileall -q -b -f .

# Expose port
EXPOSE 8080

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
