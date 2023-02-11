FROM python:3.11.1

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY ./Discord-Bot .
EXPOSE 1000
CMD [ "python", "./Discord-Bot/main.py" ]