#!/bin/bash

IP="10.0.0.140"

#curl -s --digest --user parkspass:parkspass "http://$IP/local/speedmonitor/statistics.cgi?begin=1719813600000000" > exported_statistics.csv
#scp -q root@$IP:/var/spool/storage/SD_DISK/areas/speedmonitor/\* ./

python3 statistics.py
diff statistics.csv exported_statistics.csv
if [ $? -eq 0 ]; then
  echo "GENERATED CSV IS IDENTICAL"
else
  echo "GENERATED CSV HAS DIFFERENCES"
fi
