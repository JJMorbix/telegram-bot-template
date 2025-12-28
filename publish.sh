#!/bin/bash
set -e  # interrompe se c'è un errore

# === CONFIG ===
DEV_DIR="./dev"
PROD_DIR="./prod"
BACKUP_DIR="./backups"
KEEP_BACKUPS=5
IGNORE_FILE="./.rsyncignore"

# === CREO BACKUP ===
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_PATH="$BACKUP_DIR/prod_backup_$TIMESTAMP"

echo "Creo backup di prod in $BACKUP_PATH ..."
mkdir -p "$BACKUP_PATH"
rsync -av --delete "$PROD_DIR/" "$BACKUP_PATH/"

# === PULIZIA BACKUP VECCHI ===
echo "Pulizia backup vecchi, tengo solo gli ultimi $KEEP_BACKUPS ..."
ls -1dt "$BACKUP_DIR"/* | tail -n +$((KEEP_BACKUPS+1)) | xargs -r rm -rf

# === DEPLOY NUOVO CODICE ===
echo "Deploy da dev a prod ..."
rsync -av --delete --exclude-from="$IGNORE_FILE" "$DEV_DIR/" "$PROD_DIR/"

echo "Deploy completato!"