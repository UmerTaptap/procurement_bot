cd app/
# Start rasa server with nlu model
rasa run --model models --enable-api --cors "*" --debug \
         -p $PORT

# # Start Rasa action server
# rasa run actions --debug