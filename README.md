# VFAT3-TB-Software



<h3>Installation</h3>
<br>- If the SW is used on a standalone computer, follow the MySQL installation steps. Otherwise skip the steps and ask 
Cern BD login information from the maintainer.
<br>- Instructions are for installation on a standard CentOS 7. 

<br>
<br><b>Install MySQL: (Only if using SW on standalone computer)</b>
<br><i>wget http://repo.mysql.com/mysql-community-release-el7-5.noarch.rpm</i>
<br><i>sudo rpm -ivh mysql-community-release-el7-5.noarch.rpm</i>
<br><i>sudo yum update</i>
<br><i>sudo yum install mysql-server</i>
<br><i>sudo systemctl start mysqld</i>

<br><b>Create root password: (Only if using SW on standalone computer)</b>
<br><i>sudo mysql_secure_installation</i>

<br><b>Create database and VFAT3 user: (Only if using SW on standalone computer)</b>
<br><i>mysql -u root -p</i>
<br><i>create database VFAT3_Production;</i>
<br><i>grant all on VFAT3_Production.* to 'VFAT3' identified by '1234';</i>
<br><i>exit</i>

<br>


<br><b>Install python depencies:</b>
<br><i>sudo yum install tkinter.x86_64 python-devel.x86_64 python-matplotlib scipy.x86_64 pyserial.noarch </i>
<br><i>sudo easy_install pip</i>
<br><i>sudo pip install pymysql</i>

<br><b>Install Git:</b>
<br><i>sudo yum install git</i>

<br><b>Clone software from GitHub:</b>
<br><i>git clone https://github.com/henripetrow/VFAT3-TB-Software.git</i>
<br><i>cd VFAT3-TB-Software/</i>
<br><i>git checkout new_FW</i>
<br> If using local database:
<br>python ./scripts/create_database.py</i>



<h3>Using the Software</h3>

<br><b>Launching the software</b>
<br> The software can be launched by running:
<br> <i>python GUI.py</i>

<br><b>Launch options:</b>
<br><i>-psu</i>
<br> Allows the software to control the connected power supply. Only tested with TTi PL303QMD-P power supply.
<br>
<br><i>-temp_gun</i>
<br> Use an external infrared temperature measurement for the calibration of the chips internal temperature measurement calibration. Works only Omega OS1327D.
<br>
<br><i>-encode_chipid</i>
<br>The chip ID is burned to the chip by using Reed-Muller encoding.