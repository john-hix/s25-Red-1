# Environment Variables  
before starting, make a copy of `env_dump` to `.env` and replace all values with yours  

## DBMate  
db mate connects to the existing postgresql container using the provided template in `env_dump`  
it will execute any commands for migrations by doing: `docker compose exec dbmate dbmate <command>`  
^ or add a migrations file to `dbmate/migrations` for it to migrate  
if you would like to have it always execute something when started up, add it to `./db/dbmate-entrypoint.sh`  
^ this has to be in this folder, as the folder gets mounted in the docker compose
official dbmate repository: https://github.com/amacneil/dbmate

## pgadmin
upon setup, add the server through the gui
right click servers -> register -> server
connection -> variables in .env

## resetting
to clear the current volumes, do sudo docker compose down -v
