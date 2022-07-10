FROM python:3.8

EXPOSE 3111

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

CMD ["sh", "endpoint.sh"]