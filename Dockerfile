FROM python:3.13.2-slim

WORKDIR /app
COPY ./redis_intr00der /app

EXPOSE 6339

CMD ["python", "__init__.py"]
