FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir flask requests

# Copy MCP server
COPY mcp_http_proxy.py .

# Expose port
EXPOSE 8080

CMD ["python", "mcp_http_proxy.py"]
