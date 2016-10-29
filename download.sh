#!/bin/sh
wget http://geolite.maxmind.com/download/geoip/database/GeoLite2-Country.mmdb.gz -O- | gunzip > prox/database/GeoLite2-Country.mmdb
