from flask import Flask, jsonify
import threading
import os
import json
import signal
import atexit
import logging
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()


app = Flask(__name__)

log_file = os.getenv('LOG_FILE')


logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class APIStateManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.state_file = "api_state.json"
        self.counters = self.load_state()
        
    def load_state(self):
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                logging.info("State loaded successfully")
                return state
            return {"plantid": 0, "healthid": 0}
        except Exception as e:
            logging.error(f"Error loading state: {e}")
            return {"plantid": 0, "healthid": 0}
    
    def save_state(self):
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.counters, f)
            logging.info("State saved successfully")
        except Exception as e:
            logging.error(f"Error saving state: {e}")

    def get_string_from_file(self, filename):
        try:
            with open(filename, "r") as file:
                lines = file.readlines()
                return lines[0].strip() if lines else "File is empty"
        except Exception as e:
            logging.error(f"Error reading from {filename}: {e}")
            return "Error reading file"

    def delete_first_line(self, filename):
        try:
            with open(filename, "r") as file:
                lines = file.readlines()
            with open(filename, "w") as file:
                file.writelines(lines[1:])
            logging.info(f"First line deleted from {filename}")
        except Exception as e:
            logging.error(f"Error deleting first line from {filename}: {e}")

    def count_lines(self, filename):
        try:
            with open(filename, "r") as file:
                return len(file.readlines())
        except FileNotFoundError:
            logging.warning(f"File not found: {filename}")
            return 0
        except Exception as e:
            logging.error(f"Error counting lines in {filename}: {e}")
            return 0

    def handle_request(self, api_name, filename):
        with self.lock:
            try:
                self.counters[api_name] += 1
                if self.counters[api_name] >= 2:
                    self.delete_first_line(filename)
                    self.counters[api_name] = 0
                self.save_state()  
                return {"Key": self.get_string_from_file(filename)}
            except Exception as e:
                logging.error(f"Error handling request for {api_name}: {e}")
                return {"error": "Internal server error"}

    def get_statistics(self):
        with self.lock:
            try:
                plantid_lines = self.count_lines("plantid.txt")
                healthid_lines = self.count_lines("healthid.txt")
            
                return {
                    "keys": {
                        "plantid": {
                            "keys_available": plantid_lines,
                            "status": "File is empty" if plantid_lines == 0 else "Keys available"
                        },
                        "healthid": {
                            "keys_available": healthid_lines,
                            "status": "File is empty" if healthid_lines == 0 else "Keys available"
                        },
                    },
                    "requests": {
                        "plantid": {
                            "requests_until_rotation": 100 - self.counters["plantid"]
                        },
                        "healthid": {
                            "requests_until_rotation": 100 - self.counters["healthid"]
                        },
                    }
                
                }
            except Exception as e:
                logging.error(f"Error getting statistics: {e}")
                return {"error": "Error retrieving statistics"}

state_manager = APIStateManager()

def signal_handler(signum, frame):
    logging.info("Received shutdown signal. Saving state...")
    state_manager.save_state()
    exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)
atexit.register(state_manager.save_state)

@app.route('/api/plantid', methods=['GET'])
def get_plantid():
    return jsonify(state_manager.handle_request("plantid", "plantid.txt"))

@app.route('/api/healthid', methods=['GET'])
def get_healthid():
    return jsonify(state_manager.handle_request("healthid", "healthid.txt"))

@app.route('/api/stats', methods=['GET'])
def get_stats():
    return jsonify(state_manager.get_statistics())

if __name__ == '__main__':
    try:
        app.run(debug=os.getenv('FLASK_DEBUG', 'False') == 'True', port=int(os.getenv('FLASK_RUN_PORT', 5000)))
    except Exception as e:
        logging.error(f"Application error: {e}")
        state_manager.save_state()