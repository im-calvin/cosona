
# Set the base image
FROM python:3.11.7-bookworm

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir gunicorn

# Install SQLite3
RUN apt-get update && apt-get install -y sqlite3 libsqlite3-dev

# Copy the source code
COPY . /app

# Set the main file
ENV FLASK_APP=api.py

# Expose the port
EXPOSE 8080

# Run the application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "api:app"]
