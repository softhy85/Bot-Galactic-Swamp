FROM python:3.11.2-alpine3.16

COPY ./.env ./

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY ./Discord-Bot .

CMD [ "python", "./Discord-Bot/main.py" ]