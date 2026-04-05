from flask import Flask, jsonify
from datetime import datetime
import os

app = Flask(__name__)

START_TIME = datetime.utcnow()
READY = True

@app.route("/")
def home():
    return jsonify({
        "app": "ClusterPulse",
        "message": "ClusterPulse is running",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })

@app.route("/healthz")
def healthz():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }), 200

@app.route("/ready")
def ready():
    if not READY:
        return jsonify({
            "status": "not_ready"
        }), 503

    return jsonify({
        "status": "ready",
        "uptime_seconds": int((datetime.utcnow() - START_TIME).total_seconds())
    }), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)