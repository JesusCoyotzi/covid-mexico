import pandas as pd 
import matplotlib.pyplot as plt 
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter

import datetime
import argparse
import sys

def graph_df(df,cumulative=False, title="Cases"):
  """Graph cases per dar, df has to have proper format"""
  fig, ax = plt.subplots(figsize=(15,7))

  if cumulative:      
     df = coalesced_df.cumsum()
     df.plot(grid=True,ax=ax)
  else:
     ax.bar(df.index,df['Sospechosos'],label='Sospechosos',bottom=df['Positivos'])
     ax.bar(df.index,df['Positivos'],label='Positivos')
  
  date_form = DateFormatter('%d-%m-%Y')
  ax.set_title(title)
  ax.xaxis_date()
  ax.xaxis.set_major_locator(mdates.WeekdayLocator())
  ax.xaxis.set_major_formatter(date_form)
  ax.xaxis.set_tick_params(rotation=45)
  ax.legend()
  
  
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
    estado = parsed.estado.upper()
    estado_sel = estado_df[estado_df['ENTIDAD_FEDERATIVA'] == estado]
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
  print("Casos sospechosos   || {}".format(pending_df['ID_REGISTRO'].count()))
  #active_df = covid_df[covid_df['RESULTADO'] != 3]

  #Did not used all of the categories but left code for referenced
  timeseries_full = covid_df.groupby('FECHA_SINTOMAS') 
  timeseries_positive  = positive_df.groupby('FECHA_SINTOMAS')
  timeseries_pending  = pending_df.groupby('FECHA_SINTOMAS')
  #timeseries_negative  = negative_df.groupby('FECHA_SINTOMAS')

  print("------------------------------")
  death_df = covid_df.loc[covid_df['FECHA_DEF'] != "9999-99-99"].copy()
  death_df['FECHA_DEF'] = pd.to_datetime(death_df['FECHA_DEF'],format="%Y-%m-%d")
  if parsed.desplazamiento:
    death_df = death_df[death_df['FECHA_DEF'] < last_date]

  print("Defunciones registradas ||  {}".format(death_df['ID_REGISTRO'].count()) )
  positive_death_df = death_df[death_df['RESULTADO'] == 1]
  print("Defunciones positivas   ||  {}".format(positive_death_df['ID_REGISTRO'].count()) ) 
  suspect_death_df = death_df[death_df['RESULTADO'] == 3]
  print("Defunciones sospechosas || {}".format(suspect_death_df['ID_REGISTRO'].count()) )

  death_series_full = death_df.groupby('FECHA_DEF')
  death_series_positive = positive_death_df.groupby('FECHA_DEF')
  death_series_suspect = suspect_death_df.groupby('FECHA_DEF')
  
  coalesced_deaths = pd.DataFrame(columns=["Positivos", "Sospechosos"])  
  coalesced_deaths['Positivos'] = death_series_positive['ID_REGISTRO'].count()
  coalesced_deaths['Sospechosos'] = death_series_suspect['ID_REGISTRO'].count()
   
  coalesced_df = pd.DataFrame(columns=["Positivos", "Sospechosos"])
  #coalesced_df['Total'] = timeseries_full['ID_REGISTRO'].count().cumsum()
  #coalesced_df['Negativos'] = timeseries_negative['ID_REGISTRO'].count().cumsum()
  coalesced_df['Sospechosos'] = timeseries_pending['ID_REGISTRO'].count()
  coalesced_df['Positivos'] = timeseries_positive['ID_REGISTRO'].count()
  
  #Fill days with no data or cases
  coalesced_deaths.fillna(0,inplace=True)
  coalesced_df.fillna(0,inplace=True)

  #Plotting
  plt.style.use('ggplot')
  graph_df(coalesced_df,cumulative=parsed.acumulados, title="Cases {}".format(entidad))
  graph_df(coalesced_deaths,cumulative=parsed.acumulados, title="Defunciones {}".format(entidad))
  plt.show()
