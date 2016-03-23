#!/usr/bin python
import pwd
import grp
import os
import sys
import shutil
import subprocess
from tempfile import mkstemp
from uuid import UUID
import re
import MySQLdb
import netifaces as ni

unrar_pkg = 'unrar_5.2.6-1_armhf.deb'
unrar_url = 'http://sourceforge.net/projects/bananapi/files/' + unrar_pkg

sr_repo = 'https://github.com/SickRage/SickRage.git'
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

advancedsettings_base = """<advancedsettings>
	<videodatabase>
		<type>mysql</type>
		<host>{}</host>
		<port>3306</port>
		<user>kodi</user>
		<pass>kodi</pass>
	</videodatabase>
	<videolibrary>
		<importwatchedstate>true</importwatchedstate>
		<importresumepoint>true</importresumepoint>
	</videolibrary>
</advancedsettings>
"""

def main():

	tr_usr = "osmc"
	tr_pwd = "osmc"
	download_dir = "/home/osmc/Downloads"
	incomplete_dir = "/home/osmc/Incomplete"
	media_dir_base = "/mnt/"
	media_dir = "media"

	# if not root...kick out
	if not os.geteuid()==0:
		sys.exit("\nYou must be root to run this application, please use sudo and try again.\n")

	mount_drive = raw_input("Do you want to mount an external drive (Y/N)? ")
	if mount_drive.strip() in ['y', 'Y', 'yes', 'Yes', 'YES']:
		mount_label = raw_input("Enter directory name (default is media): ")
		if len(mount_label.strip()) > 0:
			media_dir = mount_label.replace("/","")
		proceed = raw_input("Please connect your external drive and then press enter")
		p = subprocess.Popen(['sudo','blkid'])
		p.wait()
		if p.returncode == 0:
			uuid = raw_input("Enter the UUID of your external drive: ")
			if len(uuid.replace("\"","").strip()) == 36:
				#TODO: check format type automatically
				format = raw_input("Enter your disk format type (ext3, ext4, vfat, ntfs): ")
				format.strip()
				media_path = media_dir_base + media_dir
				create_dir(media_path)
				uuid_mount = 'UUID=' + uuid + '  ' + media_path + '  ' + format + '  defaults,noatime  0  0'
				confirm = raw_input("This line will be added in /etc/fstab: '" + uuid_mount + "' - Confirm? (Y/N): ")
				if confirm in ['y', 'Y', 'yes', 'Yes', 'YES']:
					with open('/etc/fstab', 'a') as fstab:
						fstab.write(uuid_mount)
						fstab.close()
					p = subprocess.Popen(['sudo','mount','-a'])
					p.wait()
					if p.returncode == 0:
						p = subprocess.Popen(['sudo','blkid'])
						p.wait()
						if p.returncode == 0:
							print 'Drive mounted!'
							print '---------------------'
				else: print 'Mounting aborted.'
			else: print 'Error: UUID provided is not valid. Mounting aborted.'

	install_transmission = raw_input("Do you want to install Transmission (Y/N) ? ")
	install_sickrage = raw_input("Do you want to install SickRage (Y/N) ? ")
	install_couchpotato = raw_input("Do you want to install CouchPotato (Y/N) ? ")
	install_mysql = raw_input("Do you want to install MySql (Y/N) ? ")

	p = subprocess.Popen(['sudo', 'apt-get', 'update'])
	p.wait()
	if p.returncode == 0:
		if install_transmission.strip() in ['y', 'Y', 'yes', 'Yes', 'YES']:
			tr_usr_input = raw_input("Enter Transmission username (Default: 'osmc') : ")
			tr_pwd_input = raw_input("Enter Transmission password (Default: 'osmc') : ")
			download_dir_input = raw_input("Enter download dir absolute path (Default: /home/osmc/Downloads): ")
			incomplete_dir_input = raw_input("Enter incomplete dir absolute path (Default: /home/osmc/Incomplete): ")

			if len(tr_usr_input.strip()) > 1:
				tr_usr = tr_usr_input
			if len(tr_pwd_input.strip()) > 1:
				tr_pwd = tr_pwd_input
			if len(download_dir_input.strip()) > 1:
				download_dir = download_dir_input
			if len(incomplete_dir_input.strip()) > 1:
				incomplete_dir = incomplete_dir_input

			if do_transmission(tr_usr, tr_pwd, download_dir, incomplete_dir):
				print 'Transmission installed!'
		if install_sickrage.strip() in ['y', 'Y', 'yes', 'Yes', 'YES']:
			if do_sickrage(unrar_url, unrar_pkg, sr_repo, sr_path):
				print 'SickRage installed!'
		if install_couchpotato.strip() in ['y', 'Y', 'yes', 'Yes', 'YES']:
			if do_couchpotato(cp_repo, cp_path):
				print 'CouchPotato installed!'
		if install_mysql.strip() in ['y', 'Y', 'yes', 'Yes', 'YES']:
			if do_mysql():
				print 'MySql installed!'
			else: print 'Error during MySql configuration'
		print 'Installation complete!'

def create_dir(path):
	if not os.path.exists(path):
		os.makedirs(path)
	elif not os.access(os.path.dirname(path), os.W_OK):
		sys.exit("Error: unable to create directory " + path);

def chown_dir(path, user, group):
	if not os.path.exists(path):
		sys.exit("Error: file not found. Unable to chmod " + path)
	else:
		uid = pwd.getpwnam(user).pw_uid
		gid = grp.getgrnam(group).gr_gid
		os.chown(path, uid, gid)

def chmod_dir(path, permissions):
	if not os.path.exists(path):
		sys.exit("Error: file not found. Unable to chown " + path)
	else:
		os.chmod(path, permissions)

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

def validate_path(path):
	norm_path = os.path.normpath(path)
	return os.path.isabs(norm_path) 

'''
def get_fs_type(mypath):
	root_type = ""
	for part in psutil.disk_partitions():
		if part.mountpoint == '/':
			root_type = part.fstype
			continue

		if mypath.startswith(part.mountpoint):
			return part.fstype
	return root_type
'''

def do_transmission(username, password, download, incomplete):
	p = subprocess.Popen(['sudo', 'apt-get', 'install', 'transmission-daemon', '-y'])
	p.wait()
	if p.returncode == 0:
		p2 = subprocess.Popen(['sudo', '/etc/init.d/transmission-daemon', 'stop'])
		p2.wait()
		if p2.returncode == 0:
			if validate_path(download):
				create_dir(download)
				chown_dir(download, "debian-transmission", "debian-transmission")
				chmod_dir(download, 511)
			else: sys.exit("Download path not valid!")
			if validate_path(incomplete):
				create_dir(incomplete)
				chown_dir(incomplete, "debian-transmission", "debian-transmission")
				chmod_dir(incomplete, 511)
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

def do_mysql():
	p = subprocess.Popen(['sudo','apt-get','install','mysql-server-5.5','-y'])
	p.wait()
	if p.returncode == 0:
		file_path = '/etc/mysql/my.cnf'
		shutil.copyfile(file_path,file_path + '.orig')
		replace_regex(file_path, 'bind-address', '#bind-address')
		p = subprocess.Popen(['sudo','service','mysql','restart'])
		p.wait()
		if p.returncode == 0:	
			print 'MySql service restarted'
			mysql_pwd = raw_input("Enter mysql password for root user: ")
			con = MySQLdb.connect('localhost', 'root', mysql_pwd.replace(" ",""))
			with con:
				cur = con.cursor()
				#cur.execute("CREATE USER 'kodi' IDENTIFIED BY 'kodi'")
				cur.execute("GRANT ALL ON *.* TO 'kodi'")
				ni.ifaddresses('eth0')
				ip = ni.ifaddresses('eth0')[2][0]['addr']
				advancedsettings = advancedsettings_base.format(ip)
				with open('advancedsettings.xml', 'w') as fout:
					fout.write(advancedsettings)
					fout.close()
				p = subprocess.Popen(['sudo', 'mv', 'advancedsettings.xml', '/home/osmc/.kodi/userdata/' + 'advancedsettings.xml'])
				p.wait()
				if p.returncode == 0:
					return True
	return False


if __name__ == "__main__":main()
