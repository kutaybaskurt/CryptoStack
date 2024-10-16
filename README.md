# CryptoStack
A Flask-based API that fetches real-time cryptocurrency prices from Binance and stores them in a PostgreSQL database. Dockerized for easy setup and deployment.
# CryptoStack

A Flask-based API that fetches real-time cryptocurrency prices from Binance and stores them in a PostgreSQL database. Dockerized for easy setup and deployment.

## Overview

CryptoStack is a simple API that retrieves real-time cryptocurrency prices from Binance, stores the data in a PostgreSQL database, and provides easy access to this data via API endpoints. The project is containerized using Docker for simple setup and scaling.

## Tech Stack

- Flask (Python)
- PostgreSQL
- Binance API
- Docker & Docker Compose

## Setup

Clone the repository and run the following command to build and start the containers:

```bash
docker-compose up --build
This command will:

Build the Docker image for the Flask app.
Set up the PostgreSQL database.
Start both services, with the Flask API available at http://localhost:5001.
API Endpoints

GET /api/test: Check if the API is running. Returns a simple message.
GET /api/<symbol>/5min: Retrieves cryptocurrency prices for the last 5 minutes.
Example:
GET /api/ETHUSDT/5min
GET /api/<symbol>/60min: Returns the average price for the given cryptocurrency over the last 60 minutes.
Example:
GET /api/ETHUSDT/60min
License

This project is licensed under the MIT License.
