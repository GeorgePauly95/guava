Guava API contracts

HTTP Endpoints

1. Start a workout

Description: This API creates a workout entry and returns its id. 

Request: 
Endpoint: /api/workouts

Successful Response: {"id": 1}

2. Stop a workout

Description: This API stops the workout.

Request:
Endpoint: /api/workouts/{workout_id}/status

Successful Response: null


Websocket Endpoint

Endpoint: /ws

1. location

Description: location information about the client, sent by the client to the server.

Message:
{
"type": "location"
"payload": {
  "latitude": -12.10,
  "longitude": 79.01,
  "timestamp": "2026-02-19T08:53:28Z",
  "workout_id": 1
  }
}

2. metrics

Description: workout metrics sent by the server to the client.

Message: 
{
"type": "metrics",
"payload": {
  "distance": 2;
  "time": 2m36s 
}
}

