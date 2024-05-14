# Use an official Python runtime as a parent image
FROM python:3.10.8-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/.vault
RUN mkdir -p /app/temp
RUN mkdir -p /app/logs

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run the application with Gunicorn
#CMD ["gunicorn", "-b", "0.0.0.0:8000", "sql_translator_api:app", "--timeout 1200" "--log-level=debug", "--log-file=/app/temp/app_log.log"]
CMD ["python", "sql_translator_api.py"]
