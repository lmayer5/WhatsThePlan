# What's The Plan? 🍻

A real-time venue traffic monitoring and analytics platform for bars and nightlife venues. Built for the college bar scene to help customers find the hottest spots and help owners understand their traffic patterns.

## Features

- **Real-time Traffic Monitoring**: Track venue occupancy in real-time via secure ingestion API
- **Analytics Dashboard**: Visualize traffic patterns with interactive charts
- **Live Campus Map**: See venue hotness scores on an interactive map
- **Mobile Web Preview**: Access the map on mobile devices
- **Simulation Mode**: Built-in traffic simulator for development/demo purposes

## Tech Stack

| Layer      | Technology                          |
|------------|-------------------------------------|
| Backend    | FastAPI (Python 3.11)               |
| Database   | PostgreSQL 15                       |
| Cache      | Redis                               |
| Worker     | Python (Redis Streams consumer)     |
| Frontend   | React + Vite + Recharts + Leaflet   |
| Mobile     | React Native (Expo) + Leaflet Web   |
| Container  | Docker Compose                      |

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Git

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/whatstheplan.git
   cd whatstheplan
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env with your own SECRET_KEY
   ```

3. **Start the services**
   ```bash
   docker-compose up --build
   ```

4. **Access the applications**
   - **API**: http://localhost:8000
   - **API Docs**: http://localhost:8000/docs
   - **Frontend Dashboard**: http://localhost:5173
   - **Mobile Web Preview**: http://localhost:19006

### Default Credentials

For development, the system seeds a default admin user:
- **Email**: `admin@example.com`
- **Password**: `changeme`

> ⚠️ **Change these in production!**

## Running the Traffic Simulation

To see the dashboard in action with simulated data:

```bash
# In a separate terminal, after docker-compose up
docker-compose exec web python simulate_traffic.py
```

This simulates a Friday night (7PM-2AM) across 5 venues with realistic traffic patterns.

## Project Structure

```
├── app/                    # FastAPI backend
│   ├── main.py            # API endpoints
│   ├── models.py          # SQLAlchemy models
│   ├── schemas.py         # Pydantic schemas
│   ├── auth.py            # JWT authentication
│   └── database.py        # DB connection
├── worker/                 # Redis stream consumer
├── frontend/              # React dashboard
├── mobile/                # React Native (Expo) app
├── docker-compose.yml     # Container orchestration
├── simulate_traffic.py    # Traffic simulation script
└── bar_agent.py           # Data ingestion agent
```

## API Endpoints

| Endpoint              | Method | Description                |
|-----------------------|--------|----------------------------|
| `/auth/login`         | POST   | Obtain JWT token           |
| `/auth/register`      | POST   | Register new user          |
| `/venues`             | GET    | List all venues            |
| `/scores`             | GET    | Get realtime hotness scores|
| `/analytics/{id}`     | GET    | Get venue analytics (auth) |
| `/ingest`             | POST   | Ingest traffic data (HMAC) |
| `/health`             | GET    | Liveness probe             |
| `/health/ready`       | GET    | Readiness probe            |

## Environment Variables

See [.env.example](.env.example) for all configuration options.

| Variable       | Description                  | Default                      |
|----------------|------------------------------|------------------------------|
| `DATABASE_URL` | PostgreSQL connection string | (See docker-compose)         |
| `REDIS_URL`    | Redis connection string      | `redis://redis:6379/0`       |
| `SECRET_KEY`   | JWT signing key              | **Must be set in production**|
| `CORS_ORIGINS` | Allowed frontend origins     | `http://localhost:5173,...`  |

## Development

### Running Tests
```bash
docker-compose exec web pytest
```

### Resetting the Database
The dashboard includes a "Restart Simulation" button that:
- Clears all transaction data
- Restarts the traffic simulation
- Resets the CSV log

## Security Notes

- Never commit `.env` files with real secrets
- Change the default admin password in production
- Use strong, randomly generated `SECRET_KEY`
- Review CORS origins for production deployment

## License

MIT License - See [LICENSE](LICENSE) for details.

## Contributing

Pull requests are welcome! Please read contributing guidelines first.

---

Built with ❤️ for the college nightlife scene
