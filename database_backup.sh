#!/usr/bin/env bash
export PATH=/bin:/usr/bin:/usr/local/bin

###############################################################
################# Update below values  ########################

source "$PWD/.env" ## Set the location and file name for your environment variables
DB_BACKUP_PATH='/backup/dbbackup' ## Local folder for where backups are stored
MYSQL_HOST='localhost'
MYSQL_PORT='3306'
BACKUP_RETAIN_DAYS=3   ## Number of days to keep local database backup copy

################################################################
################## ENV VARIABLES  ##############################

MYSQL_USER=$DB_USER
MYSQL_PASSWORD=$DB_PASSWORD
DB_BACKUP_FOLDER=$DB_BACKUP_FOLDER
DATABASE_NAME=$DB_NAME

################################################################

WORKING_DIR=$PWD
TODAYS_FOLDER=$(date +"%d%b%Y")
NAME=$(date +"%d%b%Y-%H%M")
FNAME="$DATABASE_NAME"-"$NAME".sql.gz

#################################################################
if [[ ! $DB_BACKUP_PATH ]]; then
    echo "[$(date +%d:%m:%y@%H:%M)] Creating Backup Folder"
    mkdir -p "$DB_BACKUP_PATH"
fi

mkdir -p "$DB_BACKUP_PATH"/"$TODAYS_FOLDER"
echo "Backup started for database - $DATABASE_NAME"

if mysqldump --databases --add-drop-database -h "$MYSQL_HOST" \
   -P "$MYSQL_PORT" \
   -u "$MYSQL_USER" \
   -p"$MYSQL_PASSWORD" \
   "$DATABASE_NAME" | gzip > "$DB_BACKUP_PATH"/"$TODAYS_FOLDER"/"$FNAME"; then
  echo "Database backup successfully completed"
else
  echo "Error found during backup"
  exit 1
fi

##### Remove backups older than {BACKUP_RETAIN_DAYS} days  #####

DBDELDATE=$(date +"%d%b%Y" --date="$BACKUP_RETAIN_DAYS days ago")

if [ -n "$DB_BACKUP_PATH" ]; then
      cd "$DB_BACKUP_PATH" || exit
      if [ -n "$DBDELDATE" ] && [ -d "$DBDELDATE" ]; then
            rm -rf "$DBDELDATE"
      fi
fi

if ! cd "$WORKING_DIR"; then
    echo "[$(date +%d:%m:%y@%H:%M)] Unable to navigate to the working directory"
    exit 1
fi

source venv/bin/activate
python3 "$PWD/onedrive.py" $TODAYS_FOLDER $FNAME
deactivate

# ### End of script ####
