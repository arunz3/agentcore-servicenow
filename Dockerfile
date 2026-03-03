# Use an ECR Public Python image to avoid Docker Hub rate limits
FROM public.ecr.aws/docker/library/python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent code
COPY agent.py .

# Create a cloud env file to avoid Docker ENV expansion issues with $ symbols
RUN echo "SN_INSTANCE_URL=https://dev217693.service-now.com" > .env && \
    echo "SN_USERNAME=admin" >> .env && \
    echo "SN_PASSWORD=ht/\$8qEZD5Ji" >> .env && \
    echo "AWS_REGION=us-east-1" >> .env && \
    echo "BEDROCK_MODEL_ID=us.meta.llama3-1-8b-instruct-v1:0" >> .env

# Expose the standard port
EXPOSE 8080

# Start the agent application
CMD ["python", "agent.py"]
