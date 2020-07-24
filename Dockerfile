FROM python:3.8-buster

RUN mkdir -p /opt/bot
WORKDIR /opt/bot

RUN apt-get update \
 && apt -yq install curl \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcb-dri3-0 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxtst6 \
    xdg-utils \
 && wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
 && dpkg -i google-chrome-stable_current_amd64.deb \
 && apt -yq --fix-broken install \
 && rm -rf /var/lib/apt/lists/* \
 && rm google-chrome-stable_current_amd64.deb

RUN wget https://chromedriver.storage.googleapis.com/`curl "$(google-chrome --version | awk -F ' ' '{print $3}' | awk -F '.' '{print "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_"$1}')"`/chromedriver_linux64.zip \
 && unzip chromedriver_linux64.zip \
 && cp chromedriver /usr/local/bin/chromedriver \
 && chmod a+x /usr/local/bin/chromedriver \
 && rm chromedriver_linux64.zip \
 && rm chromedriver
 
ENV DISPLAY=:99

COPY requirements.txt /opt/bot/requirements.txt
RUN pip install -r requirements.txt
COPY apollo.py /opt/bot/apollo.py
COPY apollodb.py /opt/bot/apollodb.py
COPY run.py /opt/bot/run.py

ENTRYPOINT ["python3", "run.py"]
