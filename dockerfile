FROM python:3.9.13
 
WORKDIR /app
 
COPY requirements.txt .
RUN pip install -r requirements.txt

RUN apt-get update -y
RUN apt-get install libgl1-mesa-glx libglib2.0-0 -y
 
COPY . .
 
EXPOSE 8000
CMD ["python3", "Django_Backend/backend/manage.py", "runserver", "0.0.0.0:8000"]