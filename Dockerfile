# syntax=docker/dockerfile:1

FROM selenium/standalone-firefox

WORKDIR /home/seluser
COPY . .

RUN sudo apt-get update
RUN sudo apt-get -y install pip
RUN pip install -r requirements.txt

CMD ["python3", "-u", "runner_local.py"]
