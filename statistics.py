import csv
import os
import sqlite3
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

def azimuth_label(azimuth):
  if azimuth <= 45 or azimuth >= 315:
    return 'departing'
  elif azimuth <= 135:
    return 'rightwards'
  elif azimuth <= 225:
    return 'approaching'
  else:
    return 'leftwards'

def classification(n):
  if n == 3:
    return 'Human'
  elif n == 4:
    return 'Vehicle'
  else:
    return 'Unknown'

def convert_bearing(db_bearing):
  scale = Decimal(2**15/360).quantize(Decimal('0.0000000001'))
  x = Decimal(db_bearing) / scale
  return x.quantize(0, ROUND_HALF_UP)

def convert_duration(db_duration):
  x = Decimal(db_duration) / 1000
  return x.quantize(Decimal('0.01'), ROUND_HALF_UP)

def convert_speed(db_speed):
  x = Decimal(db_speed) / 100 * Decimal('0.8') / 2
  return x.quantize(0, ROUND_HALF_UP) * 2 * Decimal('0.45')

def dict_factory(cursor, row):
  fields = [column[0] for column in cursor.description]
  return {key: value for key, value in zip(fields, row)}

connection = sqlite3.connect('statistics.db')
connection.row_factory = dict_factory
cursor = connection.cursor()
cursor.execute('SELECT * FROM Track ORDER BY start_timestamp, track_id')
rows = cursor.fetchall()
rows_out = []

for row in rows:
  row_out = {}
  rows_out.append(row_out)

  d = datetime.fromtimestamp(row['start_timestamp'] / 1000000).astimezone(timezone.utc)

  row_out['track_id']        = row['track_id']
  row_out['rmd_zone_name']   = 'Scenario {}'.format(row['profile_id'])
  row_out['trigger_count']   = row['profile_trigger_id']
  row_out['object_class']    = classification(row['classification'])
  row_out['weekday']         = d.strftime('%a')
  row_out['date']            = d.strftime('%Y-%m-%d')
  row_out['time']            = d.strftime('%H:%M:%S.%f')
  row_out['duration']        = convert_duration(row['duration'])
  row_out['enter_direction'] = azimuth_label(convert_bearing(row['enter_bearing']))
  row_out['enter_azimuth']   = convert_bearing(row['enter_bearing'])
  row_out['exit_direction']  = azimuth_label(convert_bearing(row['exit_bearing']))
  row_out['exit_azimuth']    = convert_bearing(row['exit_bearing'])
  row_out['min_speed']       = convert_speed(row['min_speed'])
  row_out['avg_speed']       = convert_speed(row['avg_speed'])
  row_out['max_speed']       = convert_speed(row['max_speed'])
  row_out['speed_delta']     = convert_speed(row['exit_speed']) - convert_speed(row['enter_speed'])
  row_out['alarm']           = (row['flags'] >> 2) & 1

with open('statistics.csv', 'w', newline='') as fout:
  dict_writer = csv.DictWriter(fout, rows_out[0].keys(), lineterminator=os.linesep)
  dict_writer.writeheader()
  dict_writer.writerows(rows_out)
