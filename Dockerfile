# Use an ECR Public Python image to avoid Docker Hub rate limits
FROM public.ecr.aws/docker/library/python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent code
COPY agent.py .
# (Optional) Copy .env for local testing, but usually handled by k8s/cloud env vars
# COPY .env .

# Expose the standard port
EXPOSE 8080

# Start the agent application
CMD ["python", "agent.py"]
