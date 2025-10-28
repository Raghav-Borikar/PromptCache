# Start from the same base Python image for consistency
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file
COPY ./requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the frontend application code
COPY . .

# Expose the port that Streamlit runs on (default is 8501)
EXPOSE 8501

# The command to run the Streamlit app when the container starts
# We use --server.address 0.0.0.0 to make it accessible outside the container
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]