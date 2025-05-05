# Use an official Python runtime as a parent image
FROM python:3.12

# Set the working directory
WORKDIR /app

# Copy only requirements first to leverage Docker's caching
COPY requirements.txt .

# Install dependencies
RUN apt-get update && apt-get install -y default-mysql-client && rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# Copy everything else
COPY . .

# Copy wait-for-mysql script and make sure it's executable
COPY wait-for-mysql.sh /wait-for-mysql.sh
RUN chmod +x /wait-for-mysql.sh

# Expose FastAPI port
EXPOSE 8095

# Use wait-for-mysql before starting FastAPI
ENTRYPOINT ["/wait-for-mysql.sh"]
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8095", "--workers", "4"]
