# Use a specific version of PostgreSQL
FROM postgres:13

# Install necessary packages
RUN apt-get update && apt-get -y install libpq-dev
ENV POSTGRES_PASSWORD=secret
ENV POSTGRES_USER=username
ENV POSTGRES_DB=database
