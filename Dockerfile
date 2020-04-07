FROM python:3-slim
#
WORKDIR /opt/app
#
COPY requirements.txt ./
COPY *.py ./
RUN pip install --no-cache-dir -r requirements.txt
#
CMD [ "python3", "./exporter.py" ]