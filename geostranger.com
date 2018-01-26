server {
    listen 80 default_server;
    listen [::]:80 default_server;

    server_name geostranger.com www.geostranger.com;

    return 301 https://$server_name$request_uri;
}

server {

    server_name geostranger.com www.geostranger.com;

    listen 443 ssl http2 default_server;
    listen [::]:443 ssl http2 default_server;

    include snippets/self-signed.conf;
    include snippets/ssl-params.conf;


   location / {
        include uwsgi_params;
        uwsgi_pass unix:///tmp/geostranger.sock;
   }
}


server {
    listen 80;
    listen [::]:80;

    server_name test.geostranger.com;

    return 301 https://$server_name$request_uri;


}

upstream tunnel {
  server 127.0.0.1:8443;
}

server {

    server_name test.geostranger.com;

    listen 443 ssl http2;
    listen [::]:443 ssl http2;

    include snippets/self-signed.conf;
    include snippets/ssl-params.conf;


    location / {
        proxy_set_header  X-Real-IP  $remote_addr;
        proxy_set_header  X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_pass http://tunnel;
    }
}