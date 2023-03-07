FROM python:3.10

WORKDIR /imobiliare_scraper

COPY requirements.txt requirements.txt

RUN apt-get update && apt-get -y upgrade
RUN apt-get -y install cron vim
RUN pip3 install -r requirements.txt

COPY crontab /etc/cron.d/crontab
COPY imobiliare_scraper .
COPY .env .

RUN chmod 0644 /etc/cron.d/crontab

RUN /usr/bin/crontab /etc/cron.d/crontab

CMD ["cron", "-f"]
