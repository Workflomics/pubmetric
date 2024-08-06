FROM python:3.9-slim AS builder

# Set the working directory in the container
WORKDIR /app

# Copy the application code into the container
COPY . .

# Install dependencies using setup.py
RUN python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir setuptools \
    && python setup.py install

# Final stage
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the application code from the builder stage
COPY --from=builder /app /app

# Expose port 8000 for the application
EXPOSE 8000

# Define environment variable
ENV PYTHONUNBUFFERED=1

# Command to run the FastAPI application
CMD ["uvicorn", "src.wfqc.api_test:app", "--host", "0.0.0.0", "--port", "8000"]
