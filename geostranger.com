server {
    listen 80 default_server;
        listen [::]:80 default_server;
    server_name geostranger.com *.geostranger.com;

    location / {
        include uwsgi_params;
        uwsgi_pass unix:///tmp/geostranger.sock;
    }
}

