# Use a lightweight Python base image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy and install the dependencies first so this layer is cached when only the code changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code and the serialized model
COPY . .

# Document the port the API listens on
EXPOSE 7860

# Start the application using Gunicorn
# - `-w 4`: uses 4 worker processes for handling requests
# - `-b 0.0.0.0:7860`: binds the server to port 7860 on all network interfaces
# - `app:superkart_api`: the Flask instance `superkart_api` inside `app.py`
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:7860", "app:superkart_api"]
