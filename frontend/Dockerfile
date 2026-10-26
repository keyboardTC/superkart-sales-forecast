# Use a minimal base image with Python 3.12 installed
FROM python:3.12-slim

# Set the working directory inside the container to /app
WORKDIR /app

# Install the Python dependencies first so this layer is cached when only the code changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Streamlit application
COPY . .

# Document the port the UI listens on
EXPOSE 8501

# Run the Streamlit app on port 8501 and make it accessible from outside the container
# (XSRF protection is disabled so file uploads work through the Codespaces port-forwarding proxy)
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableXsrfProtection=false"]
