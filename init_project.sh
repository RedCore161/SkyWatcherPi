#!/usr/bin/env bash


STANDARD_USER="pi"

# mysql-credentials
SQL_ROOT="root"
SQL_ROOT_PWD="toor"

SQL_USER="skywatcher"
SQL_PWD="xycASdjdsf_234lS_asdolkQmcy"
SQL_DB_NAME="DB_SkyWatcher"
SQL_CONFIG="/tmp/skywatcher-sql.cnf"

HOST_IP="192.168.178.20"

SECRETKEY="S3cret-Key!"

UNMOUNT_CAMERA="unmount-camera.sh"

#=========================================================

echo -n "Please check & modify the header-variables in this file! There is no error handling, so it's important!\n"
read -r -p "Have you done so? [y/N]:  " response
if ! [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]
then
    exit
fi

if [[ "$EUID" -ne 0 ]]
  then printf "Please run with sudo!\n"
  exit
fi

#=========================================================


run_cmd() {
    $1 > /dev/null;
    if [[ "$?" -eq 0 ]]
        then printf "\n\tDone!\n"
    else
        printf "\n\tFailed!\n"
    fi
}

printf "[Info] Updating sources..."
apt-get update
printf "\n\tDone!\n"

printf "[Info] Installing packages..."
apt-get install python3-pip apt-file git-core mariadb-server;
apt-get install phpmyadmin;
apt-get install build-essential cmake pkg-config libjpeg-dev libtiff5-dev\
                libjasper-dev libpng-dev libavcodec-dev libavformat-dev libswscale-dev\
                libv4l-dev libxvidcore-dev libx264-dev libhdf5-dev libhdf5-serial-dev libhdf5-103
printf "\n\tDone!\n"

#=========================================================


printf "[Info] Adding user '$STANDARD_USER' to 'www-data'-group..."
run_cmd "TODO"

#=========================================================


printf "[Info] Create python-env..."
mkdir virtualenvs
cd virtualenvs
run_cmd "virtualenv -p python3.7 skywatcher"
cd ..

printf "[Info] Activating python-env..."
run_cmd "source virtualenvs/skywatcher/bin/activate"

printf "[Info] Install python-packages"
run_cmd "pip3 install opencv-contrib-python==4.1.0.25 django-rest-auth djangorestframework mysqlclient"
#printf "[Info] Run setup.py"
#run_cmd "python3 setup.py install"

#=========================================================


printf "[Info] Deactivate canon-automount..."
printf "ATTRS{idVendor}=='04a9', ATTRS{idProduct}=='32cc', RUN+='${UNMOUNT_CAMERA}'" > /etc/udev/rules.d/canon.rules
#printf "TODO" > ${UNMOUNT_CAMERA}
chmod 755 ${UNMOUNT_CAMERA}

run_cmd "TODO"


#chmod 755 ${UNMOUNT_CAMERA}

#=========================================================

#TODO sudo mysql_secure_installation

printf "[Info] Create SQL-User '$SQL_USER' and DB '${SQL_DB_NAME}'"
`printf '[client]
user = '${SQL_ROOT}'
password = '${SQL_ROOT_PWD}'
host = localhost' > ${SQL_CONFIG}`

init_mysql=`mysql --defaults-extra-file=${SQL_CONFIG}\
                  --execute="CREATE DATABASE IF NOT EXISTS $SQL_DB_NAME;
                             CREATE USER IF NOT EXISTS '$SQL_USER'@'localhost' IDENTIFIED BY '$SQL_PWD';
                             GRANT ALL PRIVILEGES ON $SQL_DB_NAME.* TO '$SQL_USER'@'localhost' WITH GRANT OPTION;"`

run_cmd ${init_mysql}
rm ${SQL_CONFIG}


printf "[Info] Adding '/var/www/skywatcher.config'"
create_config=`printf '{
	"NAME": "'${SQL_DB_NAME}'",
        "USER": "'${SQL_USER}'",
        "PASSWORD": "'${SQL_PWD}'",
	"HOSTS": ["127.0.0.1", "'${HOST_IP}'"],
	"SECRETKEY": "'${SECRETKEY}'",
	"DEBUG": true
}' > /var/www/skywatcher_config.json`
run_cmd ${create_config}

#=========================================================


#TODO sudo modprobe v4l2loopback

#=========================================================




