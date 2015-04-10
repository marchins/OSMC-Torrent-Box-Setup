#!/bin/bash
sudo apt-get update &&
sudo git clone http://github.com/RuudBurger/CouchPotatoServer /opt/CouchPotato &&
sudo chown -R osmc:osmc /opt/CouchPotato &&
touch couchpotato.service &&
sudo echo "[Unit]" > couchpotato.service &&
sudo echo "Description=couchpotato daemon" >> couchpotato.service &&
sudo echo "" >> couchpotato.service &&
sudo echo "[Service]" >> couchpotato.service &&
sudo echo "ExecStart=/usr/bin/python /opt/CouchPotato/CouchPotato.py" >> couchpotato.service &&
sudo echo "Restart=always" >> couchpotato.service &&
sudo echo "" >> couchpotato.service &&
sudo echo "[Install]" >> couchpotato.service &&
sudo echo "WantedBy=default.target" >> couchpotato.service &&
sudo mv couchpotato.service /etc/systemd/system/couchpotato.service &&
sudo systemctl daemon-reload &&
sudo systemctl start couchpotato.service &&
sudo systemctl enable couchpotato.service