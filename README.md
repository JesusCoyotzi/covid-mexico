# Covid mexico
Script en python para graficar informacion oficial sobre COVID-19 en México
Este script permite graficar los casos confirmados y sospechosos mediante la base de datos publica de la Secretaria de Salud. Esta actualizado 
al ultimo formato modificado el dia 5 de octubre. Pero se provee otra rama compatible para el formato anterior.
Los casos sospechosos y confirmados se definen de la misma forma que en los informes tecnicos diarios. Bajo el campo de CLASIFICACION_FINAL se considera
caso positivo si fue dictaminado por comite, asociacion o si se tiene una muestra confirmada. Por otro lado se considera sospechoso si la muestra no fue
procesada, esta fue invalida o se encuentra todavía en laboratorio. Finalmente negativo en todo otro caso

## Dependencias 
Este proyecto depende solo de una version de python3 asi como matplotlib y pandas
- python 3(6.9)
- matplotlib (2.1.1)
- pandas (1.1.0)
- xlrd (1.2.0)
En mi caso esas son las versiones exactas que use pero deberia funcionar con cualquier version reciente de los anteriores.

## Uso
Puedes utilizar el script download-data.sh para descargar la version del día de la Secretaria de Salud sobre los casos de Covid

```
download-data.sh
```
Esto descarga y descomprime el archivo bajo csv_data. Se provee ademas los catalogos y descriptores dentro de este repositorio en csv_data/dic_datos_covid19
tanto los diccionarios de datos como los datos son copia directa del sitio de la Secretaria de Salud: 

[Datos abiertos covid 19](https://datos.gob.mx/busca/dataset/informacion-referente-a-casos-covid-19-en-mexico)

Una vez descargados los datos se ejecuta el script de python:

```bash
python3 covid_salubridad.py -h
usage: covid_salubridad.py [-h] [--estado ESTADO] [--catalogo CATALOGO]
                           [--desplazamiento DESPLAZAMIENTO] [--acumulados]
                           [--ingreso] [--semanal]
                           archivo

Datos oficiales Covid-18

positional arguments:
  archivo               csv con datos de la secretaria de salud

optional arguments:
  -h, --help            show this help message and exit
  --estado ESTADO
  --catalogo CATALOGO   Catalogo de datos para Covid-19
  --desplazamiento DESPLAZAMIENTO
                        Dias a omitir a partir de hoy
  --acumulados          Grafica casos acumulados en vez de incidencias
  --ingreso             Usa fecha de ingreso en lugar de fecha de sintomas
  --semanal             Grafica casos por semana en lugar día
```

Por ejemplo:
```bash
python3 covid_salubridad.py csv_data/201024COVID19MEXICO.csv
```

Esto genera dos graficas de barras una para las defunciones diarias junto a las defunciones sospechosas y otra con los casos confirmados y sospechosos.

## Parametros
Una explicacion un poco mas detallada de cada parametro en el script:

### Estado
Si este parametro se suministra se graficará solo el estado indicado, en caso de no encontrar el estado se muestra un error. El nombre debe estar correctamente 
escrito o el programa no sera capaz de encontrarlo. Para una lista de los nombres utilizados para esta base de datos favor de consultar el archivo 
csv_data/dic_datos_covid19/Catalogos_071020.xlsx

### Catalogo
Este parametro permite indicar un catalogo de datos diferente, por defecto se utiliza el archivo: csv_data/Catalogos_071020.xlsx. Dentro del script
se utiliza para leer el nombre de los estados y hacer las referencias necesarias dentro de la base de datos.

### Dezplazamiento
Generalmente los datos de los ultimos días es muy variable y cambian frecuentemente. Se pueden omitir n dias usando esta opción para asi solo mostrar 
la información
que ya esta estable

### Acumulados
Bandera que permite indicar si se graficarán los datos de casos y defunciones diarias o acumuladas. En el segundo caso la grafica se vuelve un par de curvas:
Una para sospechosos y otra para confirmados

### Ingreso
Bandera que indica que la grafica se realize en funcion de la fecha de ingreso al centro de salud en lugar de la fecha de inicio de sintomas

### Semanal
Cambia el grafico de casos diarios a casos por semana
