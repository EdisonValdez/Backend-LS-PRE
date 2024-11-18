#!/bin/sh

# A simple script to perform postgres db backup.
DATE=$(date +"%Y%m%d%H%M%S")
# TODO : Update your servername, username and database names
#gzip customerdata_${DATE}.tar
# Cleanup configuration backups older than 30 days.
#You can comment or adjust this if you donot want to delete old backups.
#find /backups/postgres_backups -name "customerdata*.gz" -mtime +30 -type f -delete

echo "Creando copia de seguridad $DATE.sql"  >> /backups/cron.log 2>&1
FILE="$DATE.sql"
if ! PGPASSWORD=$POSTGRES_PASSWORD pg_dump -h postgres -U $POSTGRES_USER --no-owner --exclude-table-data logs_webrequest $POSTGRES_DB >> /backups/$FILE
then
    echo "> [ERROR] No se ha podido crear la copia de seguridad "  >> /backups/cron.log 2>&1
    rm -f $FILE
else
    echo "> [OK] Creada correctamente "  >> /backups/cron.log 2>&1
fi

sleep 10
exec /backups_cron/dropbox.sh $FILE