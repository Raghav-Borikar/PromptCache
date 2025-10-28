# Start from a lightweight official Python image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY ./requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend source code into the container
COPY . ./backend/

# Expose the port that Uvicorn will run on
EXPOSE 8000

# The command to run the application when the container starts
# We use 0.0.0.0 to make it accessible outside the container
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]