#!/bin/sh
echo "Updating Dependencies"
apt-get update
apt-get upgrade
echo "Restarting services"
systemctl restart postgresql
pip3 install --user -U -r requirements.txt
echo "Running build"
python3 build.py