#!/bin/bash

# Script to create user and db for `Examiner` (MySQL).
set -a
source '.env'
set +a

sudo mysql -e "CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET UTF8;"
sudo mysql -e "USE $DB_NAME;"
sudo mysql -e "CREATE USER IF NOT EXISTS $DB_USER@localhost IDENTIFIED BY 'password';"
sudo mysql -e "GRANT ALL PRIVILEGES ON $DB_NAME.* TO $DB_USER@localhost;"
sudo mysql -e "REVOKE GRANT OPTION ON $DB_NAME.* FROM $DB_USER@localhost;"
sudo mysql -e "FLUSH PRIVILEGES;"

python3 src/manage.py migrate

python3 src/manage.py createsuperuser --noinput
