#!/usr/bin python
import pwd
import grp
import os
import sys
import shutil
import subprocess
from tempfile import mkstemp
import re

unrar_pkg = 'unrar_5.2.6-1_armhf.deb'
unrar_url = 'http://sourceforge.net/projects/bananapi/files/' + unrar_pkg

sr_repo = 'https://github.com/SiCKRAGETV/SickRage.git'
sr_path = '/opt/sickrage'
sr_service_content = """[Unit]
Description=Sickrage daemon

[Service]
ExecStart=/usr/bin/python /opt/sickrage/SickBeard.py
Restart=always

[Install]
WantedBy=default.target
"""

cp_repo = 'http://github.com/RuudBurger/CouchPotatoServer'
cp_path = '/opt/CouchPotato'
cp_service_content = """[Unit]
Description=CouchPotato daemon

[Service]
ExecStart=/usr/bin/python /opt/CouchPotato/CouchPotato.py
Restart=always

[Install]
WantedBy=default.target
"""

def main():
	# if not root...kick out
	if not os.geteuid()==0:
	    	sys.exit("\nYou must be root to run this application, please use sudo and try again.\n")

	tr_usr = raw_input("Enter Transmission username: ")
	tr_pwd = raw_input("Enter Transmission password: ")
	download_dir = raw_input("Enter download dir absolute path (Usually /home/osmc/Downloads): ")
	incomplete_dir = raw_input("Enter incomplete dir absolute path (Usually /home/osmc/Incomplete): ")
	p = subprocess.Popen(['sudo', 'apt-get', 'update'])
        p.wait()
        if p.returncode == 0:
		if do_transmission(tr_usr, tr_pwd, download_dir, incomplete_dir):
			if do_sickrage(unrar_url, unrar_pkg, sr_repo, sr_path):
				if do_couchpotato(cp_repo, cp_path):
					print 'Installation complete!'

def validate_path(path):
	norm_path = os.path.normpath(path)
	return os.path.isabs(norm_path) 

def create_dir(path):
	if not os.path.exists(path):
		os.makedirs(path)
	elif not os.access(os.path.dirname(path), os.W_OK):
		sys.exit("Error: unable to create directory " + path);
	
	uid = pwd.getpwnam("debian-transmission").pw_uid
	gid = grp.getgrnam("debian-transmission").gr_gid
	os.chown(path, uid, gid)
	os.chmod(path, 511)

#TODO: use only one replace method with regex
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

#def rollback():
	# sudo rm -rf download_dir
	# sudo rm -rf incomplete_dir
	# sudo rm 

def do_transmission(username, password, download, incomplete):
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

def do_sickrage(unrar_url, unrar_pkg, sr_repo, sr_path):
	p = subprocess.Popen(['sudo', 'apt-get', 'install', 'python-cheetah', 'git-core', '-y'])
        p.wait()
        if p.returncode == 0:
		p = subprocess.Popen(['wget', unrar_url])
		p.wait()
		if p.returncode == 0:
			p = subprocess.Popen(['sudo', 'dpkg', '-i', unrar_pkg])
			p.wait()
			if p.returncode == 0:
				p = subprocess.Popen(['sudo', 'rm', unrar_pkg])
				p.wait()
				if p.returncode == 0:
					p = subprocess.Popen(['sudo', 'git', 'clone', sr_repo, sr_path])
					p.wait()
					if p.returncode == 0:
						p = subprocess.Popen(['sudo', 'chown', '-R', 'osmc:osmc', sr_path])
						p.wait()
						if p.returncode == 0:
							sr_service = 'sickrage.service'
							with open(sr_service, 'w') as fout:
								fout.write(sr_service_content)
								fout.close()
							p = subprocess.Popen(['sudo', 'mv', sr_service, '/etc/systemd/system/' + sr_service])
							p.wait()
							if p.returncode == 0:
								p = subprocess.Popen(['sudo', 'systemctl', 'daemon-reload'])
								p.wait()
								if p.returncode == 0:
									p = subprocess.Popen(['sudo', 'systemctl', 'start', sr_service])
									p.wait()
									if p.returncode == 0:
										p = subprocess.Popen(['sudo', 'systemctl', 'enable', sr_service])
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
	
def do_couchpotato(cp_repo, cp_path):
	p = subprocess.Popen(['sudo', 'git', 'clone', cp_repo, cp_path])
	p.wait()
	if p.returncode == 0:
		p = subprocess.Popen(['sudo', 'chown', '-R', 'osmc:osmc', cp_path])
		p.wait()
		if p.returncode == 0:
			cp_service = 'couchpotato.service'
			with open(cp_service, 'w') as fout:
				fout.write(cp_service_content)
				fout.close()
			p = subprocess.Popen(['sudo', 'mv', cp_service, '/etc/systemd/system/' + cp_service])
			p.wait()
			if p.returncode == 0:
				p = subprocess.Popen(['sudo', 'systemctl', 'daemon-reload'])
				p.wait()
				if p.returncode == 0:
					p = subprocess.Popen(['sudo', 'systemctl', 'start', cp_service])
					p.wait()
					if p.returncode == 0:
						p = subprocess.Popen(['sudo', 'systemctl', 'enable', cp_service])
						p.wait()
						if p.returncode == 0:
							return True
						else: sys.exit('Error: unable to enable couchpotato at startup')
					else: sys.exit('Error: unable to start couchpotato service')
				else: sys.exit('Error: unable to reload service')
			else: sys.exit('Error: unable to create couchpotato.service')
		else: sys.exit('Error: unable to create couchpotato.service')
	else: sys.exit('Error: unable to clone CouchPotato repo')


if __name__ == "__main__":main()