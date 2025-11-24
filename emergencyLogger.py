import json
from flask import Flask, request, jsonify
from datetime import datetime

# app = Flask(__name__)
REDIRECT_LOG_FILE = "redirect_logs.txt"
CALLBACK_LOG_FILE = "callback_logs.txt"

def log_request_details(request,FILENAME=CALLBACK_LOG_FILE):
    """Extracts relevant request details and logs them to a file."""
    timestamp = datetime.now().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "method": request.method,
        "url": request.url,
        "headers": dict(request.headers),
        "remote_addr": request.remote_addr,
        "form_data": dict(request.form),
        "json_data": request.get_json(silent=True),
        "args": dict(request.args),
    }

    # Append the JSON representation of the log entry to the file
    with open(REDIRECT_LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry, indent=4) + "\n---\n")

    print(f"Logged request details to {REDIRECT_LOG_FILE}")

@app.route("/api/txn-callback", methods=["GET", "POST", "PUT"])
def handle_callback():
    """
    Endpoint to receive callback requests.
    It logs all request details and returns a simple success response.
    """
    log_request_details(request,CALLBACK_LOG_FILE)
    return jsonify({"status": "received", "message": "Request details logged successfully."}), 200

@app.route("/api/txn-redirect", methods=["GET", "POST", "PUT"])
def handle_redirect():
    """
    Endpoint to receive callback requests.
    It logs all request details and returns a simple success response.
    """
    log_request_details(request,REDIRECT_LOG_FILE)
    return jsonify({"status": "received", "message": "Request details logged successfully."}), 200

if __name__ == "__main__":
    # The file is created in the same directory where you run this script
    print(f"Starting Flask app. Logs will be appended to {REDIRECT_LOG_FILE} or {CALLBACK_LOG_FILE}")
    app.run(debug=True, port=5000)
