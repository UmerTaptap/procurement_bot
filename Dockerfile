# Use Rasa's official image as the base image
FROM rasa/rasa:3.0.0

# Set the working directory in the Docker container
WORKDIR /app

# Copy all the files from your local machine to the container
COPY . /app

# Install any Python dependencies (if you have a requirements.txt file)
RUN pip install --no-cache-dir -r requirements.txt

# Train the Rasa model (optional, if not pre-trained)
RUN rasa train

# Expose port 5005 to access Rasa's API
EXPOSE 5005

# Start the Rasa server with API enabled and CORS set to "*"
CMD ["rasa", "run", "--enable-api", "--cors", "*", "--port", "5005"]
