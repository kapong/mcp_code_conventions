FROM python:3.12-slim

WORKDIR /app

RUN pip install uv

COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

COPY . .

# Ensure data directory exists and copy default data
RUN mkdir -p /app/data
COPY app/data/ /app/data/

# Copy tools configuration
COPY app/tools.json /app/tools.json

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]