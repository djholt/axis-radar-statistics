import csv
import numpy as np
import sqlite3

def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}

connection = sqlite3.connect('statistics.db')
connection.row_factory = dict_factory
cursor = connection.cursor()
cursor.execute('SELECT * FROM Track ORDER BY start_timestamp, track_id')
rows = cursor.fetchall()

with open('exported_statistics.csv', 'r') as f:
  csv_rows = list(csv.DictReader(f))

x = []
y = []
for i in range(len(rows)):
  db_row = rows[i]
  csv_row = csv_rows[i]
  x.append(db_row['enter_bearing'])
  y.append(int(csv_row['enter_azimuth']))
  x.append(db_row['exit_bearing'])
  y.append(int(csv_row['exit_azimuth']))

x = np.array(x)
y = np.array(y)
n = np.size(x)
x_mean = np.mean(x)
y_mean = np.mean(y)

Sxy = np.sum(x*y)-n*x_mean*y_mean
Sxx = np.sum(x*x)-n*x_mean*x_mean

b1 = Sxy/Sxx
b0 = y_mean-b1*x_mean
print('slope:', b1)
print('intercept:', b0)
