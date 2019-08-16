FROM debian:10

ENV DEBIAN_FRONTEND noninteractive
ENV ES_JAVA_OPTS="-Xms1024m -Xmx1024m" ELASTICSEARCH_USERNAME=elastic ELASTICSEARCH_PASSWORD=elastic

RUN apt-get update && \
apt-get install -y --fix-missing default-jdk apt-transport-https nginx apache2-utils wget gnupg2 && \
rm -rf /var/lib/apt/lists/*

RUN wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | apt-key add - && \
echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | tee -a /etc/apt/sources.list.d/elastic-7.x.list

RUN apt-get update  -y && apt-get -y install elasticsearch kibana logstash filebeat apm-server

RUN apt-get install -y procps curl nano lsof

RUN update-rc.d elasticsearch defaults 95 10
RUN update-rc.d kibana defaults 95 10
RUN update-rc.d apm-server defaults 95 10

RUN filebeat modules enable logstash

RUN chown -R elasticsearch /usr/share/elasticsearch/*
RUN chown -R apm-server /usr/share/apm-server/*

ADD ./elasticsearch.yml /etc/elasticsearch/elasticsearch.yml
ADD ./kibana.yml /etc/kibana/kibana.yml
ADD ./logstash.yml /etc/logstash/logstash.yml
ADD ./logstash.yml /usr/share/logstash/logstash.yml
ADD ./filebeat.yml /usr/share/filebeat/filebeat.yml
ADD ./logstash.conf /etc/logstash/conf.d/logstash.conf
ADD ./apm-server.yml /etc/apm-server/apm-server.yml
ADD ./nginx.conf /etc/nginx/sites-enabled/default

RUN mkdir -p /opt/elastic

WORKDIR /opt/elastic/
COPY . /opt/elastic/

#9200 - elasticsearch
#9600 - logstash
#5601 - kibana
#8200 - APM
#90 - nginx

EXPOSE 9200 9600 5601 8200 90

CMD ["./elasticsearch-setup.sh"]
