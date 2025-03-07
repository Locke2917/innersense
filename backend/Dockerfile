# Use Python 3.11 as the base image
FROM python:3.11

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

#docker run -it --rm -v //c/users/clock/development/innersense/backend:/app -p 8000:8000 innersense-backend /bin/bash