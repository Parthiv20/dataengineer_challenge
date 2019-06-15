FROM thinkwhere/gdal-python:3.6-shippable

WORKDIR /code

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .

