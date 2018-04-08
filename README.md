# pcoip-pool-manager
## Development instance
To run the auto-updating backend script copy the env file into the project's root directory:
```
cp docker/dev.env .env
```
Then run docker compose
```
docker-compose up
```

This will build the image. If you want to build again (eg. when requirements.txt has changed) just type:
```
docker-compose up --build
```

React application can be started with:
```
cd web
yarn start
```
