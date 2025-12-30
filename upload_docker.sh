echo "Building docker flask app..."
docker build -t flask-app .
echo "Running docker flask app..."
docker run -p 3000:3000 -d -w "/app" -v "$(pwd)":/app flask-app 
echo "Flask app is running on port 3000."
echo "Checking if the app is up..."
sleep 5
curl http://localhost:3000/ 
# Check if the curl command was successful
if [ $? -eq 0 ]; then
  echo "Flask app is up and running!"
else
  echo "Failed to reach the Flask app."
  sleep 2
  echo "Checking logs..."
  docker logs $(docker ps -q --filter ancestor=flask-app)
fi
