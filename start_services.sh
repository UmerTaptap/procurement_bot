cd app/

# Start Rasa server with NLU model
rasa run --endpoints endpoints.yml --enable-api --debug --cors "*" -p $PORT

# Optional: Start the Rasa action server if you have custom actions
rasa run actions --debug &

# Wait for background jobs to complete
wait
