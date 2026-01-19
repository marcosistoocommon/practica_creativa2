FROM python:3.9-slim

WORKDIR /app

COPY bookinfo/src/productpage/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY bookinfo/src/productpage/ ./

EXPOSE 8080


CMD ["python3", "productpage_monolith.py", "8080"]