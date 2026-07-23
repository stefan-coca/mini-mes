from flask import Flask, render_template, jsonify
from database import get_machine_status
from datetime import datetime, time
from database import get_current_shift, get_shift_count

app = Flask(__name__)

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/api/status")
def api_status():
    return jsonify(get_machine_status())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

