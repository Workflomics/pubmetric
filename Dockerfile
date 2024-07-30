FROM python:3.9-slim AS builder

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt requirements.txt

# Install any dependencies
RUN python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Run any necessary build commands (if needed)
# For example, compiling assets, running tests, etc.

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

# Command to run the application
CMD ["python", "api-controller.py"]
