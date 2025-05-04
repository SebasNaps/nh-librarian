# Use a minimal Python base image
FROM python:3.11-slim

# Default environment variables (can be overridden at runtime)
ENV FLASK_ENV=production \
    PORT=5000

# Set working directory inside the container
# WORKDIR /usr/src/app
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code into the container
COPY . .

# Expose the application port
EXPOSE 5000

# Use Gunicorn with Eventlet to serve the app, binding to the specified PORT
# CMD ["gunicorn", "-k", "eventlet", "-w", "1", "-b", "0.0.0.0:5000", "run:app"]

CMD ["python", "run.py", "web"]