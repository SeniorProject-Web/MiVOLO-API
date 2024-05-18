## Install Dependencies
```
pip install -r requirements.txt
```
## Run Server
```
cd Django_Backend/backend
python manage.py runserver
```

## Build With Docker
```
docker build -t ai_demographic .
docker compose -f "docker.compose.yaml" up --scale ai_api=3
```
