#!/bin/bash

yes Y | ./bin/elasticsearch-keystore create

echo "${ELASTICSEARCH_PASSWORD}" > ./elastic-password.txt

cat ./elastic-password.txt | ./bin/elasticsearch-keystore add --stdin "bootstrap.password"
