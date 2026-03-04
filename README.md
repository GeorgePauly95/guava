Guava API contracts

HTTP

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


Websocket

Endpoint: /ws


