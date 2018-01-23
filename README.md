
## Update servers:
operationexodus:
cd /to/service/
git pull
pip install -r requirements.txt


sudo systemctl restart geostranger.service

## For new servers:

su operationexodus
cd /home/operationexodus/
git clone git@bitbucket.org:getstranger/geostranger.git geostranger

mkdir /var/log/geostranger
chown operationexodus:www-data /var/log/geostranger/

sudo pip install virtualenv
virtualenv geostrangerenv
source geostrangerenv/bin/activate

pip install -r requirements.txt
# test if work python geostranger.py
deactivate # the env

# using root
sudo cp geostranger.service /etc/systemd/system/geostranger.service
sudo systemctl start geostranger
sudo systemctl enable geostranger

sudo cp geostranger.com /etc/nginx/sites-available/geostranger.com
sudo ln -s /etc/nginx/sites-available/geostranger.com /etc/nginx/sites-enabled

sudo nginx -t # testing...

sudo systemctl restart nginx




/etc/profile
export SECRET_KEY=sd32f13w2123r13423513425332sadf1
export URL_KEY=
export TELEGRAM_BOT_KEY=
export STRANGERGEO_KEY=
export KIK_BOT_KEY=


