# cd app/

# # Start Rasa server with NLU model
# rasa run --endpoints endpoints.yml --enable-api --cors "*" --debug -p $PORT &

# # Optional: Start the Rasa action server if you have custom actions
# rasa run actions --port 5000 --debug &


#!/bin/bash

# Navigate to the app directory
cd app/

# Step 1: Train the Rasa model
echo "Training the Rasa model..."
rasa train

# Check if the training was successful
if [ $? -ne 0 ]; then
  echo "Model training failed. Exiting."
  exit 1
fi

# Step 2: Start the Rasa server with NLU model
echo "Starting the Rasa server..."
rasa run --endpoints endpoints.yml --enable-api --cors "*" --debug -p $PORT &

# Step 3: Optionally start the Rasa action server if you have custom actions
echo "Starting the Rasa action server..."
rasa run actions --port 5000 --debug &

# Wait for the background processes to finish
wait
