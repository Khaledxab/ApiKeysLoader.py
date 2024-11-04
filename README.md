# API Key Management System with Discord Bot

A comprehensive system for managing and monitoring API keys with a Flask backend server and a Discord bot for real-time monitoring.

## 🌟 Features

### API Server
- Manages two types of API keys: Plant ID and Health ID
- Automatic key rotation system
- State persistence across server restarts
- Statistics endpoint for monitoring key usage
- Thread-safe operations with proper locking mechanisms
- Comprehensive logging system

### Discord Bot
- Real-time monitoring of API key statistics
- Dynamic status updates showing available keys
- Command-based statistics retrieval
- Embedded rich messages for better data visualization
- Automatic refresh of statistics every 5 minutes

## 🚀 Setup

### Prerequisites
- Python 3.7+
- Flask
- Discord.py
- aiohttp
- python-dotenv

### Installation

1. Clone the repository:
```bash
git clone [https://khaledbenabderrahmen@bitbucket.org/ifarming/apikeysloader.py.git]
cd [apikeysloader.py]
```

2. Install required packages:
```bash
pip install flask discord.py aiohttp python-dotenv
```

3. Create a `.env` file in the project root with the following variables:
```env
# API Server Configuration
LOG_FILE=api_server.log
FLASK_DEBUG=False
FLASK_RUN_PORT=5000

# Discord Bot Configuration
DISCORD_BOT_TOKEN=discord_bot_token
STATS_API=http://localhost:5000/api/stats
```

## 📝 Configuration

### API Server
- Create two text files in the project root:
  - `plantid.txt`: Store Plant ID API keys (one per line)
  - `healthid.txt`: Store Health ID API keys (one per line)
- The server maintains state in `api_state.json`


## 🔧 Usage

### Starting the API Server
```bash
python app.py
```

The server will start on the configured port (default: 5000) with the following endpoints:
- GET `/api/plantid`: Retrieve a Plant ID key
- GET `/api/healthid`: Retrieve a Health ID key
- GET `/api/stats`: Get current statistics

### Starting the Discord Bot
```bash
python bot.py
```

### Discord Commands
- `!stats`: Display current API statistics in an embedded message

## 📊 Monitoring

The Discord bot provides real-time monitoring through:
- Bot status showing current available keys
- Statistics command for detailed information
- Automatic updates every 5 minutes
- Rich embeds showing:
  - Available keys for both services
  - Current status of key files
  - Requests remaining until next key rotation


## 💻 Development

### API Server Structure
- `APIStateManager`: Core class managing state and key rotation
- Thread-safe operations using `threading.Lock`
- Graceful shutdown handling with proper state saving
- Comprehensive error logging

### Discord Bot Structure
- Asynchronous design using discord.py
- Background tasks for status updates
- Error handling for API communication
- Customizable refresh intervals

## 📝 Logging

The API server logs important events to the configured log file, including:
- State loading/saving operations
- File operations
- Error conditions
- Server start/stop events

## ⚠️ Error Handling

Both components include comprehensive error handling for:
- File operations
- API communication
- State management
- Network issues


