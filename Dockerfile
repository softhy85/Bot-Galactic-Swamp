FROM python:3.11.2-alpine3.16

WORKDIR ./Discord-Bot

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./main.py" ]