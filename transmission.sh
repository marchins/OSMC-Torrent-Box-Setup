#!/bin/bash
sudo apt-get update &&
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
sudo /etc/init.d/transmission-daemon start