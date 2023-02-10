FROM python:3.11.2-alpine3.16

COPY ./.env ./
WORKDIR ./Discord-Bot

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "./main.py" ]