FROM python:3.9

ENV PYTHONIOENCODING=utf-8

WORKDIR /app

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python", "app.py"]