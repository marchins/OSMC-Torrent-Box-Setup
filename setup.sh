#!/bin/bash
sudo apt-get update &&
#install transmission
sudo apt-get install transmission-daemon -y &&
sudo /etc/init.d/transmission-daemon stop &&
sudo mkdir /home/osmc/Downloads &&
sudo mkdir /home/osmc/Incomplete &&
sudo chown debian-transmission:debian-transmission /home/osmc/Downloads &&
sudo chown debian-transmission:debian-transmission /home/osmc/Incomplete &&
sudo chmod 777 /home/osmc/Incomplete &&
sudo chmod 777 /home/osmc/Downloads &&
sudo cp /etc/transmission-daemon/settings.json /etc/transmission-daemon/settings.json.orig &&
sudo sed -i "s:/var/lib/transmission-daemon/downloads:/home/osmc/Downloads:" /etc/transmission-daemon/settings.json &&
sudo sed -i "s:\"incomplete-dir\".*:\"incomplete-dir\"\: \"/home/osmc/Incomplete\",:" /etc/transmission-daemon/settings.json &&
sudo sed -i "s:\"incomplete-dir-enabled\".*:\"incomplete-dir-enabled\"\: \"true\",:" /etc/transmission-daemon/settings.json &&
sudo sed -i "s:\"rpc-password\".*:\"rpc-password\"\: \"osmc\",:" /etc/transmission-daemon/settings.json &&
sudo sed -i "s:\"rpc-username\".*:\"rpc-username\"\: \"osmc\",:" /etc/transmission-daemon/settings.json &&
sudo sed -i "s:\"rpc-whitelist-enabled\".*:\"rpc-whitelist-enabled\"\: \"false\",:" /etc/transmission-daemon/settings.json &&
sudo usermod -a -G osmc debian-transmission &&
sudo /etc/init.d/transmission-daemon start &&
#install sickrage
sudo apt-get install python-cheetah git-core -y &&
wget http://sourceforge.net/projects/bananapi/files/unrar_5.2.6-1_armhf.deb &&
sudo dpkg -i unrar_5.2.6-1_armhf.deb &&
sudo rm unrar_5.2.6-1_armhf.deb &&
sudo git clone https://github.com/SiCKRAGETV/SickRage.git /opt/sickrage &&
sudo chown -R osmc:osmc /opt/sickrage &&
touch sickrage.service &&
sudo echo "[Unit]" > sickrage.service &&
sudo echo "Description=Sickrage daemon" >> sickrage.service &&
sudo echo "" >> sickrage.service &&
sudo echo "[Service]" >> sickrage.service &&
sudo echo "ExecStart=/usr/bin/python /opt/sickrage/SickBeard.py" >> sickrage.service &&
sudo echo "Restart=always" >> sickrage.service &&
sudo echo "" >> sickrage.service &&
sudo echo "[Install]" >> sickrage.service &&
sudo echo "WantedBy=default.target" >> sickrage.service &&
sudo mv sickrage.service /etc/systemd/system/sickrage.service &&
sudo systemctl daemon-reload &&
sudo systemctl start sickrage.service &&
sudo systemctl enable sickrage.service &&
#install couchpotato
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