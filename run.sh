xhost localhost
source env/env
cd docker
docker compose --env-file ../env/env run --env ../env/env pipeline