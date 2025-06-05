FROM python:3.12

RUN mkdir /src

ENV PYTHONUNBUFFERED=1
RUN apt-get update && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN python -m pip install --upgrade pip && python -m pip install --no-deps --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]