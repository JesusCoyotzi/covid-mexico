import pandas as pd 
import matplotlib.pyplot as plt 
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter

import datetime
import argparse
import sys

def graph_df(df,cumulative=False, title="Cases", bar_width=0.8):
  """Graph cases per dar, df has to have proper format"""
  fig, ax = plt.subplots(figsize=(15,7))

  if cumulative:      
     df = df.cumsum()
     df.plot(grid=True,ax=ax)
  else:
     ax.bar(df.index,df['Sospechosos'],label='Sospechosos',bottom=df['Positivos'],width=bar_width)
     ax.bar(df.index,df['Positivos'],label='Positivos',width=bar_width)
  
  date_form = DateFormatter('%d-%m-%Y')
  ax.set_title(title)
  ax.xaxis_date()
  ax.xaxis.set_major_locator(mdates.WeekdayLocator())
  ax.xaxis.set_major_formatter(date_form)
  ax.xaxis.set_tick_params(rotation=45)
  ax.legend()
  
 
def parse_df(covid_df, grouping):
  """Parse datafram into format to count cases per day"""
  #Separate into positive cases, both laboratory confirmed and ruled
  result_tag='CLASIFICACION_FINAL'
  all_positives = covid_df[result_tag].isin([1,2,3]) 
  all_suspects = covid_df[result_tag].isin([4,5,6])
  
  coalesced_df = pd.DataFrame(columns=["Positivos", "Sospechosos"])
  coalesced_df['Positivos'] = covid_df[all_positives].groupby(grouping)['ID_REGISTRO'].count()
  coalesced_df['Sospechosos'] = covid_df[all_suspects].groupby(grouping)['ID_REGISTRO'].count()
 
  return coalesced_df 

  
 
if __name__=='__main__':

  parser = argparse.ArgumentParser(description="Datos oficiales Covid-18")
  parser.add_argument('--estado',action='store',default=None)
  parser.add_argument('archivo',action='store', help='csv con datos de la secretaria de salud')
  parser.add_argument('--catalogo', action='store',default='csv_data/dic_datos_covid19/Catalogos_071020.xlsx', help='Catalogo de datos para Covid-19')
  parser.add_argument('--desplazamiento',action='store', default=0, help='Dias a omitir a partir de hoy', type=int)
  parser.add_argument('--acumulados',action='store_true', help="Grafica casos acumulados en vez de incidencias")
  parser.add_argument('--ingreso',action='store_true', help="Usa fecha de ingreso en lugar de fecha de sintomas")
  parser.add_argument('--semanal',action='store_true',help="Grafica casos por semana en lugar día")
  parsed = parser.parse_args()
 
  with pd.ExcelFile(parsed.catalogo) as xls:
    #print(xls.sheet_names)
    municipio_df = pd.read_excel(xls,'Catálogo MUNICIPIOS',index_col=0)
    estado_df = pd.read_excel(xls,'Catálogo de ENTIDADES',index_col=0)

  #print(municipio_df.head())
  #print(estado_df.head())
      
  covid_df = pd.read_csv(parsed.archivo,encoding='latin-1')
  
  if parsed.ingreso:
    date_tag="FECHA_INGRESO"  
  else:
    date_tag='FECHA_SINTOMAS'

  covid_df[date_tag] = pd.to_datetime(covid_df[date_tag])

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
    covid_df = covid_df[covid_df[date_tag] < last_date]

  if parsed.semanal:
    grouping = pd.Grouper(key=date_tag,freq="1W")
    dead_grouping = pd.Grouper(key="FECHA_DEF",freq="1W")
    bar_w = 1.5
  else:
    grouping = date_tag
    dead_grouping = "FECHA_DEF"
    bar_w = 0.5

  result_tag = 'CLASIFICACION_FINAL'
  all_positives = covid_df[result_tag].isin([1,2,3])
  all_suspects = covid_df[result_tag].isin([4,5,6])
  print("Resumen para {}".format(entidad.capitalize()))
  print("Eventos registrados || {}".format(covid_df['ID_REGISTRO'].count()))
  positive_df = covid_df[all_positives]
  print("Casos positivos     || {}".format(positive_df['ID_REGISTRO'].count()))
  negative_df = covid_df[covid_df[result_tag] == 7]
  print("Casos negativos     || {}".format(negative_df['ID_REGISTRO'].count()))
  pending_df = covid_df[all_suspects]
  print("Casos sospechosos   || {}".format(pending_df['ID_REGISTRO'].count()))
  #active_df = covid_df[covid_df['RESULTADO'] != 3]

  print("Primer caso en:     || {}".format(min(positive_df[date_tag]) ))
  print("Ultimo caso en:     || {}".format(max(positive_df[date_tag]) ))

  #Did not used all of the categories but left code for reference
  #timeseries_full = covid_df.groupby(date_tag) 
  timeseries_positive  = positive_df.groupby(grouping)
  timeseries_pending  = pending_df.groupby(grouping)
  #timeseries_negative  = negative_df.groupby('FECHA_SINTOMAS')

  print("------------------------------")
  death_df = covid_df.loc[covid_df['FECHA_DEF'] != "9999-99-99"].copy()
  death_df['FECHA_DEF'] = pd.to_datetime(death_df['FECHA_DEF'],format="%Y-%m-%d")
  if parsed.desplazamiento:
    death_df = death_df[death_df['FECHA_DEF'] < last_date]

  all_positive_deaths = death_df[result_tag].isin([1,2,3])
  all_suspect_deaths = death_df[result_tag].isin([4,5,6])
  print("Defunciones registradas ||  {}".format(death_df['ID_REGISTRO'].count()) )
  positive_death_df = death_df[all_positive_deaths]
  print("Defunciones positivas   ||  {}".format(positive_death_df['ID_REGISTRO'].count()) ) 
  suspect_death_df = death_df[all_suspect_deaths]
  print("Defunciones sospechosas || {}".format(suspect_death_df['ID_REGISTRO'].count()) )

  print("Primer defuncion en:    || {}".format(min(death_df[date_tag]) ))
  print("Ultima defuncion en:    || {}".format(max(death_df[date_tag]) ))
  #death_series_full = death_df.groupby('FECHA_DEF')
  death_series_positive = positive_death_df.groupby(dead_grouping)
  death_series_suspect = suspect_death_df.groupby(dead_grouping)
  
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
  graph_df(coalesced_df,cumulative=parsed.acumulados, title="Casos {}".format(entidad),bar_width=bar_w)
  graph_df(coalesced_deaths,cumulative=parsed.acumulados, title="Defunciones {}".format(entidad),bar_width=bar_w)
  plt.show()
