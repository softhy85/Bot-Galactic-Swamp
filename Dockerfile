FROM python:3.11.1

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY .env .
COPY ./Discord-Bot .
EXPOSE 1000
CMD [ "python", "./main.py" ]