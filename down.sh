xhost -localhost
source env/env
cd docker
docker compose --env-file ../env/env down