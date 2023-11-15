# Use an official Python runtime as the base image
FROM python:3.10-slim
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2
# Set the working directory in the container
WORKDIR /myapp

# Copy the requirements file and install dependencies

RUN pip install --upgrade pip
RUN apt-get update
# Copy the requirements file and install dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
# Copy the entire project directory into the container
COPY . .

# Specify the command to run your Django app
CMD ["cd", "store"]