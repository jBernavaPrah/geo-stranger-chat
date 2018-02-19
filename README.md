## For traductions:

pybabel extract -F babel.cfg -o messages.pot .  
pybabel update -i messages.pot -d translations
*after translate with poedit*

pybabel compile -d translations




## Update servers:
operationexodus:
cd /to/service/
source geostrangerenv/bin/activate
git pull
pip install -r requirements.txt
deactivate


sudo systemctl restart geostranger.service

 sudo journalctl -u geostranger.service --since "1 hour ago" -f

https://unix.stackexchange.com/a/225407

## For new servers:

 https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uwsgi-and-nginx-on-ubuntu-16-04

sudo apt-get update
apt-get install build-essential libssl-dev libffi-dev python-dev python-pip python-dev nginx

su operationexodus
cd /home/operationexodus/
git clone git@bitbucket.org:getstranger/geostranger.git geostranger

mkdir /var/log/geostranger
chown operationexodus:www-data /var/log/geostranger/

sudo pip install virtualenv
virtualenv -p python3 geostrangerenv
source geostrangerenv/bin/activate

pip install -r requirements.txt
# test if work python geostranger.py
deactivate # the env

# using root
sudo cp geostranger.service /etc/systemd/system/geostranger.service
sudo systemctl start geostranger
sudo systemctl enable geostranger


sudo rm -rf /etc/nginx/sites-enabled/default

sudo cp geostranger.com /etc/nginx/sites-available/geostranger.com
sudo ln -s /etc/nginx/sites-available/geostranger.com /etc/nginx/sites-enabled

sudo nginx -t # testing if all ok...

sudo systemctl restart nginx



mv geostranger.conf.example geostranger.conf
nano geostranger.conf
SECRET_KEY=
URL_KEY=
TELEGRAM_BOT_KEY=
STRANGERGEO_KEY=
KIK_BOT_KEY=


