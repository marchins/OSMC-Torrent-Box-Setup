#!/usr/bin python
import pwd
import grp
import os
import sys
import shutil
import subprocess
from tempfile import mkstemp
import re

transmission_username = None
transmission_password = None
download_dir = None
incomplete_dir = None

sr_service = """[Unit]
Description=Sickrage daemon

[Service]
ExecStart=/usr/bin/python /opt/sickrage/SickBeard.py
Restart=always

[Install]
WantedBy=default.target
"""
cp_service = """

"""


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
	download_dir = raw_input("Enter download dir absolute path (Usually /home/osmc/Downloads): ")
	incomplete_dir = raw_input("Enter incomplete dir absolute path (Usually /home/osmc/Incomplete): ")
	p = subprocess.Popen(['sudo', 'apt-get', 'update'])
        p.wait()
        if p.returncode == 0:
		if do_transmission(transmission_username, transmission_password, download_dir, incomplete_dir):
			if do_sickrage():
				#do_couchpotato()

def validate_path(path):
	#check whether the directory exists or not and if i have write permissions
	if os.path.isdir(path):
		sys.exit("Error: " + path + " already exists")
	elif os.access(os.path.dirname(path), os.W_OK):
		return True
	else: sys.exit("Error: " + path + " already exists") 

def create_dir(path):
	#create the actual directories
	os.makedirs(path)
	uid = pwd.getpwnam("debian-transmission").pw_uid
	gid = grp.getgrnam("debian-transmission").gr_gid
	os.chown(path, uid, gid)
	os.chmod(path, 511)

def replace(file_path, pattern, subst):
	fh, abs_path = mkstemp()
	with open(abs_path, 'w') as new_file:
		with open(file_path) as old_file:
			for line in old_file:
				new_file.write(line.replace(pattern, subst))
	os.close(fh)
	os.remove(file_path)
	shutil.move(abs_path, file_path)

def replace_regex(file_path, pattern, subst):
	regex = re.compile(pattern, re.IGNORECASE)
	fh, abs_path = mkstemp()
	with open(abs_path, 'w') as new_file:
		with open(file_path) as old_file:
			for line in old_file:
				new_file.write(regex.sub(subst, line))
	os.close(fh)
	os.remove(file_path)
	shutil.move(abs_path, file_path)

def do_transmission(username, password, download, incomplete):
	#transmission installation and configuration procedure
	p = subprocess.Popen(['sudo', 'apt-get', 'install', 'transmission-daemon', '-y'])
	p.wait()
	if p.returncode == 0:
		p2 = subprocess.Popen(['sudo', '/etc/init.d/transmission-daemon', 'stop'])
		p2.wait()
		if p2.returncode == 0:
			if validate_path(download):
				create_dir(download)
			else: sys.exit("Download path not valid!")
			if validate_path(incomplete):
				create_dir(incomplete)
			else: sys.exit("Incomplete path not valid!")
			file_path = '/etc/transmission-daemon/settings.json'
			shutil.copyfile(file_path,file_path + '.orig')
			subst = '"download-dir": "%s"' % download
			replace(file_path, '"download-dir": "/var/lib/transmission-daemon/downloads"', subst)
			subst = '"incomplete-dir": "%s"' % incomplete
			replace(file_path, '"incomplete-dir": "/var/lib/transmission-daemon/Downloads"', subst)
			replace(file_path, '"incomplete-dir-enabled": false', '"incomplete-dir-enabled": true')
			subst = '"rpc-username": "%s"' % username
			replace(file_path, '"rpc-username": "transmission"', subst)
			replace(file_path, '"rpc-whitelist-enabled": true', '"rpc-whitelist-enabled": false')		
			subst = '"rpc-password": "%s",' % password
			replace_regex(file_path, '"rpc-password".*', subst)
			p3 = subprocess.Popen(['sudo', 'usermod', '-a', '-G', 'osmc', 'debian-transmission'])
			p3.wait()
			if p3.returncode == 0:
				p4 = subprocess.Popen(['sudo', 'chown', 'debian-transmission:debian-transmission', file_path])
				p4.wait()
				if p4.returncode == 0:
					p5 = subprocess.Popen(['sudo', '/etc/init.d/transmission-daemon', 'start'])
					p5.wait()
					if p5.returncode == 0:
						return True
					else: sys.exit("Error: unable to start transmission daemon")
				else: sys.exit("Error: unable to chown settings.json")
			else: sys.exit("Error: unable to add debian-transmission user to group osmc")
		else: sys.exit("Error: unable to stop transmission service")
	else: sys.exit("Error: unable to install transmission-daemon")

def do_sickrage():
	p = subprocess.Popen(['sudo', 'apt-get', 'install', 'python-cheetah', 'git-core', '-y'])
        p.wait()
        if p.returncode == 0:
		p = subprocess.Popen(['wget', 'http://sourceforge.net/projects/bananapi/files/unrar_5.2.6-1_armhf.deb'])
		p.wait()
		if p.returncode == 0:
			p = subprocess.Popen(['sudo', 'dpkg', '-i', 'unrar_5.2.6-1_armhf.deb'])
			p.wait()
			if p.returncode == 0:
				p = subprocess.Popen(['sudo', 'rm', 'unrar_5.2.6-1_armhf.deb'])
				p.wait()
				if p.returncode == 0:
					p = subprocess.Popen(['sudo', 'git', 'clone', 'https://github.com/SiCKRAGETV/SickRage.git', '/opt/sickrage'])
					p.wait()
					if p.returncode == 0:
						p = subprocess.Popen(['sudo', 'chown', '-R', 'osmc:osmc', '/opt/sickrage'])
						p.wait()
						if p.returncode == 0:
							fname = 'sickrage.service'
							with open(fname, 'w') as fout:
								fout.write(sr_service)
								fout.close()
							p = subprocess.Popen(['sudo', 'mv', 'sickrage.service', '/etc/systemd/system/sickrage.service'])
							p.wait()
							if p.returncode == 0:
								p = subprocess.Popen(['sudo', 'systemctl', 'daemon-reload'])
								p.wait()
								if p.returncode == 0:
									p = subprocess.Popen(['sudo', 'systemctl', 'start', 'sickrage.service'])
									p.wait()
									if p.returncode == 0:
										p = subprocess.Popen(['sudo', 'systemctl', 'enable', 'sickrage.service'])
										p.wait()
										if p.returncode == 0:
											return True
										else: sys.exit('Error: unable to enable sickrage at startup')
									else: sys.exit('Error: unable to start sickrage service')
								else: sys.exit('Error: unable to reload service')
							else: sys.exit('Error: unable to create sickrage.service')
						else: sys.exit('Error: unable to create sickrage.service')
					else: sys.exit('Error: unable to clone Sickrage repo')
				else: pass
			else: sys.exit('Error: unable to install unrar')
		else: sys.exit('Error: unable to install unrar')
	else: sys.exit('Error: unable to install git-core')
	
#def do_couchpotato():

if __name__ == "__main__":main()