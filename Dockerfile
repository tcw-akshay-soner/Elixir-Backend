# Use an official Python runtime as a parent image
FROM python:3.12

# Set the working directory in the container
WORKDIR /

# Copy the project files into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Expose the FastAPI port (default: 8000)
EXPOSE 8095

# Command to run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8095"]
