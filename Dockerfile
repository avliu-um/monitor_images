# syntax=docker/dockerfile:1
FROM python
WORKDIR /code

COPY . .

RUN pip3 install --upgrade pip
RUN pip install -r requirements.txt
RUN apt update && apt install -y chromium-driver

CMD ["python", "./test.py"]

