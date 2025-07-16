# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Copy the server script
COPY main.py .

# Create a non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Change ownership of the app directory
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port 8080
EXPOSE 8080

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Health check to ensure the server is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import socket; s = socket.socket(); s.settimeout(5); s.connect(('localhost', 8080)); s.close()" || exit 1

# Run the server
CMD ["python", "main.py"] 