# Use official Python image
FROM python:3.11

# Copy only server requirements first (for caching)
COPY server/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy server files
COPY server/ .

# Expose FastAPI default port
EXPOSE 8000

# Run the server with Uvicorn
CMD ["uvicorn", "main:app", "--host", "server", "--port", "8000"]

