#!/bin/bash
rm -f *zip
wget "http://187.191.75.115/gobmx/salud/datos_abiertos/datos_abiertos_covid19.zip"
unzip "datos_abiertos_covid19.zip"
mv *.csv csv_data

