# cd app/

# # Start Rasa server with NLU model
# rasa run --model models --enable-api --cors “*” --debug -p $PORT &

# # Optional: Start the Rasa action server if you have custom actions
# rasa run actions --port 5000 --debug &

cd app/
# Start rasa server with nlu model
rasa run --model models --enable-api --cors "*" --debug \
         -p $PORT