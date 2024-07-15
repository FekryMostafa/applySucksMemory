FROM --platform=linux/amd64 python:3.11-bookworm

# Set the working directory in the container
WORKDIR /app

# Copy the local code to the container
COPY . .

# Install any additional Python dependencies your project might have
RUN pip install --no-cache-dir -r requirements.txt

# Ensure Python outputs are sent straight to terminal without being buffered
ENV PYTHONUNBUFFERED True

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Run the application with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]