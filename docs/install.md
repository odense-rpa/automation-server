# Installing Automation Server

Automation Server has been designed to be run in docker containers. This guide will assume that you are attempting to install on a linux machine with docker.

## Step 1 - Create your dockerfile



```
version: '3.8'

x-worker-common: &worker-template
  image: ghcr.io/odense-rpa/automation-server-worker:0.1.0
  environment:
    - ATS_URL=http://api:8000
    - ATS_TOKEN=
    - TZ=Europe/Copenhagen
  networks:
    - app-network
  depends_on:
    - api

services:
  db:
    image: postgres:latest
    environment:
      # Set a default user / password for the api. Change this for production use.
      POSTGRES_USER: ats_user 
      POSTGRES_PASSWORD: ats_password
      POSTGRES_DB: ats
    ports:
      - "5432"
    networks:
      - app-network
    volumes:
      - db-data:/var/lib/postgresql/data  # Mount named volume to /var/lib/postgresql/data
  api:
    image: ghcr.io/odense-rpa/automation-server-backend:0.1.0
    depends_on:
      - db
    ports:
      - "8000"
    environment:
      - TZ=Europe/Copenhagen
      # Remember to set username and password for production use
      - DATABASE_URL=postgresql://ats_user:ats_password@db:5432/ats
    networks:
      - app-network

  frontend:
    image: ghcr.io/odense-rpa/automation-server-frontend:0.1.0
    ports:
      - "80"
    networks:
      - app-network
    environment:
      - TZ=Europe/Copenhagen

  proxy:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - api
      - frontend
    networks:
      - app-network

  worker01:
    <<: *worker-template
    hostname: worker-01

  worker02:
    <<: *worker-template
    hostname: worker-02

networks:
  app-network:
    driver: bridge

volumes:
  db-data:

```

Our template docker file includes 2 workers to process scripts. You should adjust the number of workers to match your system requirements. There is also section on building custom workers.

## Step 2 - configure the nginx proxy

This step is only nessecary if you wish to use a custom ssl certificate, but it is very much recommended to use https even for internalt use.

This is a baseline nginx.conf that can be used.

````
events {}

http {
    upstream api {
        server api:8000;
    }

    upstream frontend {
        server frontend:80;
    }

    server {
        listen 80;
        #listen 443 ssl;

        location /api/ {
            proxy_pass http://api/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}

````

## Step 3 - Running for the first time

At this point you should have a folder on your machine containing:

* docker-compose.yml
* nginx.conf


At this point you can start Automation Server with the command:

````
docker-compose up
````

Run this command an note the output, any issues with your configuration. If you are comfortable with your configuration go ahead and run it in the background with:

````
docker-compose up -d
````

## Step 4 - Initial configuration

TODO
