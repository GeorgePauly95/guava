# Guava API

Guava is a backend service for a real-time fitness and workout tracking application. It provides RESTful APIs for managing workouts, ingesting fitness data, and a WebSocket interface for streaming real-time location and returning live metrics.

## Features

- **Workout Management**: Start and stop workout sessions.
- **Real-time Tracking**: WebSocket integration for streaming live geolocation data and receiving calculated metrics (distance, elapsed time).
- **Generic Data Ingestion**: Flexible JSON endpoint for ingesting various fitness data metrics.
- **Authentication**: Secure Google OAuth integration and JWT-based session management.

## Tech Stack

- **Framework**: FastAPI (Python)
- **Database**: SQL Database with Alembic for migrations
- **Real-time**: WebSockets

## Getting Started

### Prerequisites

- Python 3.9+
- A running SQL database (configured via `.env`)
- Google OAuth credentials

### Installation

1. Clone the repository and navigate to the project directory:
   ```bash
   git clone <repo-url>
   cd guava
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Set up the environment variables:
   Create a `.env` file in the root directory and configure your database URI and Google OAuth credentials.

4. Run database migrations:
   ```bash
   alembic upgrade head
   ```

### Running the Server

Start the development server using uvicorn:
```bash
uvicorn main:app --reload
```
The API will be available at `http://localhost:8000`. 
FastAPI automatically generates interactive API documentation. You can view it at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Documentation

### HTTP Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/workouts` | `POST` | Creates a new workout session and returns its ID. (Response: `{"id": 1}`) |
| `/api/workouts/{workout_id}/status` | `POST` / `PUT` | Updates the status of a workout (e.g., to stop the workout). |
| `/api/data` | `POST` | Ingest arbitrary fitness data in JSON format for a user. |
| `/api/v1/login` | `GET` | Initiates the Google OAuth login flow. |

### WebSocket Connections

**Endpoint:** `/ws`

Requires a valid JWT token passed for authentication. Used for bidirectional real-time streaming during a workout.

#### Client to Server: Location Updates
Send location information to the server:
```json
{
  "type": "location",
  "payload": {
    "latitude": -12.10,
    "longitude": 79.01,
    "timestamp": "2026-02-19T08:53:28Z",
    "workout_id": 1
  }
}
```

#### Server to Client: Live Metrics
The server will stream back calculated workout metrics:
```json
{
  "type": "metrics",
  "payload": {
    "distance": 2,
    "time": "2m36s" 
  }
}
```

## Contributing

Please adhere to the coding standards and ensure tests pass before submitting a pull request.
