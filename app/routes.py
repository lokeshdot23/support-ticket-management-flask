from flask import Blueprint, jsonify

from app.database import get_db_connection


main = Blueprint("main", __name__)


@main.route("/")
def home():
    return jsonify({
        "message": "Support Ticket Management API"
    })


@main.route("/api/health")
def health_check():

    connection = get_db_connection()

    if connection:
        connection.close()

        return jsonify({
            "status": "success",
            "message": "API and database are working"
        })

    return jsonify({
        "status": "error",
        "message": "Database connection failed"
    }), 500
