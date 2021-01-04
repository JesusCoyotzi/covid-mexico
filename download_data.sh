#!/bin/bash
rm -f *zip
#List of previously working addresses for the record
#wget "http://187.191.75.115/gobmx/salud/datos_abiertos/datos_abiertos_covid19.zip"
#wget "http://epidemiologia.salud.gob.mx/gobmx/salud/datos_abiertos/datos_abiertos_covid19.zip"
wget http://datosabiertos.salud.gob.mx/gobmx/salud/datos_abiertos/datos_abiertos_covid19.zip
unzip "datos_abiertos_covid19.zip"
mv *.csv csv_data


