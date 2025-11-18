# Use the official Python 3.10 image [cite: 124]
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY ./src /app/src

# Expose the port the app runs on
EXPOSE 8000

# Set the default command to run uvicorn
# The API app is in src/api/main.py [cite: 161, 198]
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]