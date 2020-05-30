import pandas as pd 
import matplotlib.pyplot as plt 

import datetime
import argparse
import sys
if __name__=='__main__':

  parser = argparse.ArgumentParser(description="Datos oficiales Covid-19")
  parser.add_argument('--estado',action='store',default=None)
  parser.add_argument('archivo',action='store', help='csv con datos de la secretaria de salud')
  parser.add_argument('--catalogo', action='store',default='csv_data/Catalogos_0412.xlsx', help='Catalogo de datos para Covid-19')
  parser.add_argument('--desplazamiento',action='store', default=0, help='Dias a omitir a partir de hoy', type=int)
  parser.add_argument('--acumulados',action='store_true', help="Grafica casos acumulados en vez de incidencias")
  parsed = parser.parse_args()
 
  with pd.ExcelFile(parsed.catalogo) as xls:
    #print(xls.sheet_names)
    municipio_df = pd.read_excel(xls,'Catálogo MUNICIPIOS',index_col=0)
    estado_df = pd.read_excel(xls,'Catálogo de ENTIDADES',index_col=0)

  #print(municipio_df.head())
  #print(estado_df.head())
      
  covid_df = pd.read_csv(parsed.archivo,encoding='latin-1')
  covid_df['FECHA_SINTOMAS'] = pd.to_datetime(covid_df['FECHA_SINTOMAS'])

  if parsed.estado:
    estado_sel = estado_df[estado_df['ENTIDAD_FEDERATIVA'] == parsed.estado]
    if estado_sel.empty:
      print("El estado {} no existe, favor de verificar".format(parsed.estado))
      sys.exit(1)
    entidad = estado_sel['ENTIDAD_FEDERATIVA'].iloc[0]
    estado_id = estado_sel.index[0]
    covid_df = covid_df[covid_df['ENTIDAD_RES'] == estado_id]
  else:
    entidad = "Estados Unidos Méxicanos"
        

  if parsed.desplazamiento:
    last_date = pd.Timestamp.now() - pd.Timedelta(days=parsed.desplazamiento)
    covid_df = covid_df[covid_df['FECHA_SINTOMAS'] < last_date]

  print("Resumen para {}".format(entidad.capitalize()))
  print("Eventos registrados || {}".format(covid_df['ID_REGISTRO'].count()))
  positive_df = covid_df[covid_df['RESULTADO'] == 1]
  print("Casos positivos     || {}".format(positive_df['ID_REGISTRO'].count()))
  negative_df = covid_df[covid_df['RESULTADO'] == 2]
  print("Casos negativos     || {}".format(negative_df['ID_REGISTRO'].count()))
  pending_df = covid_df[covid_df['RESULTADO'] == 3]
  print("Casos pendientes    || {}".format(pending_df['ID_REGISTRO'].count()))
 
  #Did not used all of the categories but left code for referenced
  timeseries_full = covid_df.groupby('FECHA_SINTOMAS') 
  timeseries_positive  = positive_df.groupby('FECHA_SINTOMAS')
  #timeseries_negative  = negative_df.groupby('FECHA_SINTOMAS')
  #timeseries_pending  = pending_df.groupby('FECHA_SINTOMAS')

  death_df = covid_df.loc[covid_df['FECHA_DEF'] != "9999-99-99"].copy()
  death_df['FECHA_DEF'] = pd.to_datetime(death_df['FECHA_DEF'],format="%Y-%m-%d")
  death_df = death_df.groupby('FECHA_DEF')

  coalesced_df = pd.DataFrame(columns=["Positivos", "Defunciones"])

  #coalesced_df['Total'] = timeseries_full['ID_REGISTRO'].count().cumsum()
  #coalesced_df['Negativos'] = timeseries_negative['ID_REGISTRO'].count().cumsum()
  #coalesced_df['Pendientes'] = timeseries_pending['ID_REGISTRO'].count()
  coalesced_df['Positivos'] = timeseries_positive['ID_REGISTRO'].count()
  coalesced_df['Defunciones'] = death_df['ID_REGISTRO'].count()
  coalesced_df.fillna(0,inplace=True)
  
  cumulative_df = coalesced_df.cumsum()

  plt.style.use('ggplot')
  if parsed.acumulados:
     ax = cumulative_df.plot(grid=True)
  else:
     ax = coalesced_df.plot(grid=True)
  ax.grid('on')
  ax.set_title('Casos {}'.format(entidad))
  plt.show()
  
