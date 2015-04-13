#!/usr/bin python
import pwd
import grp
import os
import sys
import shutil

transmission_username = None
transmission_password = None
download_dir = None
incomplete_dir = None

def main():

	# if not root...kick out
	if not os.geteuid()==0:
	    	sys.exit("\nYou must be root to run this application, please use sudo and try again.\n")

	global transmission_username
	global transmission_password
	global incomplete_dir
	global download_dir

	transmission_username = raw_input("Enter Transmission username: ")
	transmission_password = raw_input("Enter Transmission password: ")
	download_dir = raw_input("Enter download dir absolute path: (Usually /home/osmc/Downloads)")
	incomplete_dir = raw_input("Enter incomplete dir absolute path: (Usually /home/osmc/Incomplete)")

	do_transmission(transmission_username, transmission_password, download_dir, incomplete_dir)

	#do_sickrage()
	#do_couchpotato()


def validate_path(path):
	if os.access(os.path.dirname(path), os.W_OK):
		return True
	else: return False

def create_dir(path):
	os.makedirs(path)
	uid = pwd.getpwnam("debian-transmission").pw_uid
	gid = grp.getgrnam("debian-transmission").gr_gid
	os.chown(path, uid, gid)
	os.chmod(path, 511)


def do_transmission(username, password, download, incomplete):

	if validate_path(download):
	    	create_dir(download)
    	else: sys.exit("Download path not valid!")

	if validate_path(incomplete):
    		create_dir(incomplete)
    	else: sys.exit("Incomplete path not valid!")

	os.system("sudo apt-get install transmission-daemon -y")
	os.system("sudo /etc/init.d/transmission-daemon stop")

    #copy settings.json to settings.json.orig
	copyfile("/etc/transmission-daemon/settings.json","/etc/transmission-daemon/settings.json.sample")
    #modify settings.json with given username, password, download path and incomplete path

    #sudo usermod -a -G osmc debian-transmission

    #sudo /etc/init.d/transmission-daemon start



#def do_sickrage():

#def do_couchpotato():

main()

