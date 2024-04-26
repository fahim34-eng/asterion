FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install libpq-dev gcc -y
RUN pip install --upgrade pip
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY . .

ARG URL
ENV DB_URL=$DB_URL

CMD ["uvicorn", "app.main:app", "--port=8000", "--host=0.0.0.0"]