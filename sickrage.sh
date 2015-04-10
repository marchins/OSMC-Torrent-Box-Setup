#!/bin/bash
sudo apt-get update &&
sudo apt-get install python-cheetah git-core -y &&
wget http://sourceforge.net/projects/bananapi/files/unrar_5.2.6-1_armhf.deb &&
sudo dpkg -i unrar_5.2.6-1_armhf.deb &&
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
sudo systemctl enable sickrage.service