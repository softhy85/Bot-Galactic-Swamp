FROM python:3.11.1

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY ./Discord-Bot .

CMD [ "python", "./main.py" ]