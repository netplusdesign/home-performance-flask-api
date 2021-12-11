# syntax=docker/dockerfile:1
FROM home-performance-python-mariadb:v1.0.0
COPY requirements.txt .
RUN pip3 install -r requirements.txt

WORKDIR /Users/larry/projects/home-performance-flask-api/
COPY . .

EXPOSE 5000

ENTRYPOINT [ "/usr/bin/python3" ]
CMD [ "run.py" ]