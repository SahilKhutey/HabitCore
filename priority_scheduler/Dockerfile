FROM python:3.10-slim

WORKDIR /app

# Copy requirements if any, or just install dependencies directly
# Based on main.py, we need kafka-python, redis, sqlalchemy, psycopg2-binary
RUN pip install --no-cache-dir kafka-python redis sqlalchemy psycopg2-binary

COPY . .

# We need to access backend models, so we might need to mount or copy them.
# In the priority_scheduler/main.py, it imports from app.models.user.
# This suggests priority_scheduler expects to be in a structure where 'app' is available.

CMD ["python", "main.py"]
