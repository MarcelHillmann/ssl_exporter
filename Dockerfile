FROM python:3-alpine

WORKDIR /opt/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY *.py ./
CMD [ "python", "./your-daemon-or-script.py" ]