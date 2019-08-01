FROM ubuntu:18.04

#MAINTAINER Ivan Subotic "ivan.subotic@unibas.ch"
MAINTAINER Shane Seaton "shane.seaton@csiro.au"

# Silence debconf messages
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

# Install.
RUN \
  sed -i 's/# \(.*multiverse$\)/\1/g' /etc/apt/sources.list && \
  apt-get -qq update && \
  apt-get -y install \
    byobu curl git htop man vim wget unzip \
    openjdk-8-jdk && \
  rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV APP_HOME='/app'
ENV JAVA_HOME="/usr/lib/jvm/java-8-openjdk-amd64"

WORKDIR ${APP_HOME}

RUN wget https://loci-assets.s3-ap-southeast-2.amazonaws.com/script-resources/graph-cache/graphdb-free-8.10.0-dist.zip -O ${APP_HOME}/graphdb.zip
RUN unzip ${APP_HOME}/graphdb.zip -d ${APP_HOME}/graphdb && \
    mv ${APP_HOME}/graphdb/graphdb-free-8.10.0 /graphdb

# Set GraphDB Max and Min Heap size
ENV GDB_HEAP_SIZE="4g"

#Import the data
ENV GRAPHDBSOURCE=${GRAPHDBSOURCE:-"/tmp/cachedata"}
WORKDIR ${GRAPHDBSOURCE}
COPY download-data.sh ${APP_HOME}
WORKDIR ${APP_HOME}
RUN ./download-data.sh

EXPOSE 7200
CMD ["/graphdb/bin/graphdb"]