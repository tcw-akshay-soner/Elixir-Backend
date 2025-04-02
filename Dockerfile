# ✅ Correct Syntax for Python Image
FROM python:3.12 

# Set working directory
WORKDIR /app

# Copy only requirements first (for caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy all FastAPI project files
COPY . .

# Expose FastAPI port
EXPOSE 8095

# Run FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8095", "--workers", "4"]
