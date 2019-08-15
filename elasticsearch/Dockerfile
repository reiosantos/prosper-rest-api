FROM debian:10

ENV DEBIAN_FRONTEND noninteractive
ENV ES_JAVA_OPTS="-Xms1024m -Xmx1024m" ELASTICSEARCH_USERNAME=elastic ELASTICSEARCH_PASSWORD=elastic

RUN apt-get update && \
apt-get install -y --fix-missing default-jdk apt-transport-https nginx apache2-utils wget gnupg2 && \
rm -rf /var/lib/apt/lists/*

RUN wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | apt-key add - && \
echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | tee -a /etc/apt/sources.list.d/elastic-7.x.list

RUN apt-get update  -y && apt-get -y install elasticsearch kibana logstash

RUN apt-get install -y procps curl nano lsof

RUN update-rc.d elasticsearch defaults 95 10
RUN update-rc.d kibana defaults 95 10

RUN chown -R elasticsearch /usr/share/elasticsearch/*

ADD ./elasticsearch.yml /etc/elasticsearch/elasticsearch.yml
ADD ./kibana.yml /etc/kibana/kibana.yml
ADD ./logstash.yml /etc/logstash/logstash.yml
ADD ./logstash.yml /usr/share/logstash/logstash.yml
ADD ./logstash.conf /etc/logstash/conf.d/logstash.conf
ADD ./nginx.conf /etc/nginx/sites-enabled/default

RUN mkdir -p /opt/elastic

WORKDIR /opt/elastic/
COPY . /opt/elastic/

EXPOSE 9200 9600 5601 90

CMD ["./elasticsearch-setup.sh"]
