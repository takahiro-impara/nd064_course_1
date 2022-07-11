FROM python:2.7

EXPOSE 3111

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

CMD ["sh", "endpoint.sh"]