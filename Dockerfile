# Stage 1: Build Stage
FROM python:3.9 AS builder
WORKDIR /app
RUN apt-get update && \
	apt-get install -y --no-install-recommends gcc default-libmysqlclient-dev pkg-config && \
	rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
	
# Stage 2: Final Stage
FROM python:3.9-slim
WORKDIR /app
RUN apt-get update && \
	apt-get install -y --no-install-recommends libmariadb3 && \
	rm -rf /var/lib/apt/lists/*
COPY --from=builder /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/
COPY . .
CMD ["python", "app.py"]