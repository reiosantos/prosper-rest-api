#!/bin/bash

LS_JAVA_OPTS="$(echo --add-opens=java.base/{java.lang,java.security,java.util,java.security.cert,java.util.zip,java.lang.reflect,java.util.regex,java.net,java.io,java.lang}=ALL-UNNAMED) --illegal-access=warn"

export LS_JAVA_OPTS

mkdir /usr/share/elasticsearch/data/

chown -R elasticsearch /usr/share/elasticsearch/*
chown -R logstash /usr/share/logstash/*
chown -R kibana /usr/share/kibana/*
chown -R filebeat /usr/share/filebeat/*

yes Y | /usr/share/elasticsearch/bin/elasticsearch-keystore create
yes Y | /usr/share/logstash/bin/logstash-keystore create --path.settings /etc/logstash
yes Y | /usr/share/kibana/bin/kibana-keystore create --allow-root
yes Y | /usr/share/apm-server/bin/apm-server keystore create

echo -n "${ELASTICSEARCH_USERNAME}:" >> /etc/nginx/.htpasswd
echo "${ELASTICSEARCH_PASSWORD}" | openssl passwd -stdin >> /etc/nginx/.htpasswd

# setup user for elasticsearch
echo -n "${ELASTICSEARCH_PASSWORD}" > ./elastic-password.txt
cat ./elastic-password.txt | /usr/share/elasticsearch/bin/elasticsearch-keystore add --stdin "bootstrap.password"

# setup filebeats
echo "${ELASTICSEARCH_USERNAME}" | /usr/share/filebeat/bin/filebeat keystore add ELASTICSEARCH_USERNAME --stdin --force
echo "${ELASTICSEARCH_PASSWORD}" | /usr/share/filebeat/bin/filebeat keystore add ELASTICSEARCH_PASSWORD --stdin --force

# setup APM
echo "${ELASTICSEARCH_USERNAME}" | /usr/share/apm-server/bin/apm-server keystore add ELASTICSEARCH_USERNAME --stdin --force
echo "${ELASTICSEARCH_PASSWORD}" | /usr/share/apm-server/bin/apm-server keystore add ELASTICSEARCH_PASSWORD --stdin --force

# setup user for logstash
echo "${ELASTICSEARCH_USERNAME}" | /usr/share/logstash/bin/logstash-keystore add ELASTICSEARCH_USERNAME --path.settings /etc/logstash/
echo "${ELASTICSEARCH_PASSWORD}" | /usr/share/logstash/bin/logstash-keystore add ELASTICSEARCH_PASSWORD --path.settings /etc/logstash/

# setup auth for kibana
echo "${ELASTICSEARCH_USERNAME}" | /usr/share/kibana/bin/kibana-keystore add elasticsearch.username --allow-root
echo "${ELASTICSEARCH_PASSWORD}" | /usr/share/kibana/bin/kibana-keystore add elasticsearch.password --allow-root

filebeat modules enable logstash
filebeat modules enable elasticsearch

service elasticsearch start
service kibana start
service filebeat start
service nginx restart

/usr/share/apm-server/bin/apm-server &

/usr/share/logstash/bin/logstash --path.settings /etc/logstash
