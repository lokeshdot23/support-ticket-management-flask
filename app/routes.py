from flask import Blueprint, jsonify, current_app

main = Blueprint("main", __name__)


@main.route("/")
def home():
    return jsonify({
        "message": "Ticket Management System API is running",
        "secret_key_loaded": bool(current_app.config.get("SECRET_KEY"))
    })
