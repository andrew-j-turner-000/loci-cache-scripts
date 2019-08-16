FROM python:3

RUN apt-get install -y git
RUN pip3 install awscli==1.16.218

ENV APP_HOME='/usr/src/app'
WORKDIR ${APP_HOME}
COPY resources/main.sh .

CMD ["/bin/bash", "-c", "${APP_HOME}/main.sh"]