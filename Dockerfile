FROM python:3.8-buster

RUN mkdir -p /opt/bot
WORKDIR /opt/bot

RUN apt-get update
 && wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
 && dpkg -i google-chrome-stable_current_amd64.deb
 && apt -yq --fix-broken install
 && apt -yq install curl
 && rm -rf /var/lib/apt/lists/*
 && rm google-chrome-stable_current_amd64.deb

RUN wget https://chromedriver.storage.googleapis.com/`curl https://chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
 && unzip chromedriver_linux64.zip
 && cp chromedriver /usr/bin/chromedriver
 && chmod a+x /usr/bin/chromedriver
 && rm chromedriver_linux64.zip
 && rm chromedriver
 
COPY requirements.txt /opt/bot/requirements.txt
RUN pip install -r requirements.txt
COPY apollo.py /opt/bot/apollo.py
COPY apollodb.py /opt/bot/apollodb.py
COPY run.py /opt/bot/run.py

ENTRYPOINT ["python3", "run.py"]