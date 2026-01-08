FROM python:3.9-slim

WORKDIR /app

# Install dependencies first (better layer caching)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# The application listens on 8080 inside the container
EXPOSE 8080

# Start the monolithic product page on port 8080
CMD ["python3", "productpage_monolith.py", "8080"]
