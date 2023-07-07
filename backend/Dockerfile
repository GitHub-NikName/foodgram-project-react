FROM python:3.11-alpine3.18

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk add --no-cache netcat-openbsd

WORKDIR /app

COPY ./requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt --no-cache-dir
COPY . .
#RUN chmod 777 /app/entrypoint.sh
#ENTRYPOINT ["/app/entrypoint.sh"]
#CMD ["gunicorn", "--bind", "0.0.0.0:8000", "foodgram.wsgi"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]