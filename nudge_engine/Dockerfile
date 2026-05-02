FROM python:3.10

WORKDIR /app

# Install dependencies
COPY nudge_engine/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY nudge_engine/app ./app
COPY backend/app/core ./backend/app/core
COPY backend/app/models ./backend/app/models

ENV PYTHONPATH=/app:/backend

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]
