# Use slim image — smaller attack surface, faster pulls
FROM python:3.11-slim

# Don't run as root — security best practice
RUN useradd --create-home appuser
WORKDIR /app

# Copy requirements first — Docker layer caching
# If requirements.txt doesn't change, this layer is reused
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .

# Switch to non-root user
USER appuser

EXPOSE 8000

# Health check baked into the image
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
