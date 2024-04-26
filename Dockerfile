FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install libpq-dev gcc -y
RUN pip install --upgrade pip
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY . .

ARG URL
ENV DB_URL=$DB_URL
ENV AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
ENV AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY

CMD ["uvicorn", "app.main:app", "--port=8000", "--host=0.0.0.0"]