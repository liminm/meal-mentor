FROM python:3.11-slim

WORKDIR /app

RUN pip install pipenv

COPY data/data.csv data/data.csv
COPY static /app/static
COPY .env /app/.env

COPY ["Pipfile", "Pipfile.lock", "./"]

RUN pipenv install --deploy --ignore-pipfile --system

COPY meal_mentor /app/meal_mentor

EXPOSE 8000

CMD ["uvicorn", "meal_mentor.app:app", "--host", "0.0.0.0", "--port", "8000"]
