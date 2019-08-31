#/bin/sh
host="192.168.100.106"
user="postgres"
password="postgres"
dbname="everydb2"
port="5432"

year=2019
monthday=0901

python3 makequery.py --host $host --user $user --password $password --dbname $dbname --port $port --year $year --monthday $monthday
# python3 makequery.py --host $host --user $user --password $password --dbname $dbname --port $port --year $year --monthday $monthday --updateonly true