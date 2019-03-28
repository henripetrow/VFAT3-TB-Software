# VFAT3-TB-Software



<h3>Installation</h3>
<br>- If the SW is used on a standalone computer, follow the MySQL installation steps. Otherwise skip the steps and ask 
Cern BD login information from the maintainer.
<br>- Instructions are for installation on a standard CentOS 7. 

<br>
<br><b>Install MySQL: (Only if using SW on standalone computer)</b>
<br>wget http://repo.mysql.com/mysql-community-release-el7-5.noarch.rpm
<br>sudo rpm -ivh mysql-community-release-el7-5.noarch.rpm
<br>sudo yum update
<br>sudo yum install mysql-server
<br>sudo systemctl start mysqld

<br><b>Create root password: (Only if using SW on standalone computer)</b>
<br>sudo mysql_secure_installation

<br><b>Create database and VFAT3 user: (Only if using SW on standalone computer)</b>
<br>mysql -u root -p
<br>create database VFAT3_Production;
<br>grant all on VFAT3_Production.* to 'VFAT3' identified by '1234';
<br>exit

<br>


<br><b>Install python depencies:</b>
<br>sudo yum install tkinter.x86_64 python-devel.x86_64 python-matplotlib scipy.x86_64 pyserial.noarch 
<br>sudo easy_install pip
<br>sudo pip install pymysql

<br><b>Install Git:</b>
<br>sudo yum install git

<br><b>Clone software from GitHub and launch it:</b>
<br>git clone https://github.com/henripetrow/VFAT3-TB-Software.git
<br>cd VFAT3-TB-Software/
<br>git checkout new_FW
<br>python ./scripts/create_database.py
<br>python GUI.py -no_psu
