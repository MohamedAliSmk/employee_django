# The first instruction is what image we want to base our container on
# We Use an official Python runtime as a parent image
FROM python:3.10
# The enviroment variable ensures that the python output is set straight
# to the terminal with out buffering it first
# ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Set the working directory to /app
WORKDIR /app
# Install dependencies
COPY requirements.txt /app/
RUN pip install -r requirements.txt
# Copy the project code into the container
COPY . /app/
# EXPOSE 8000
