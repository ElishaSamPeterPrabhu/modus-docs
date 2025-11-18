# Modus Documentation MCP Server Dockerfile
# Python 3.13.5 base image

FROM python:3.13.5-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=8080

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY modus_docs_server.py .
COPY docs/ ./docs/
COPY component-docs/ ./component-docs/

# Expose the server port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8080/health')" || exit 1

# Run the MCP server
CMD ["python", "modus_docs_server.py"]

