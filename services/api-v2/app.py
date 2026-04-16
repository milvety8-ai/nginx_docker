import os
import socket

from flask import Flask, jsonify, request


def create_app() -> Flask:
    app = Flask(__name__)

    service_version = os.getenv("SERVICE_VERSION", "unknown")
    service_color = os.getenv("SERVICE_COLOR", "gray")

    @app.get("/")
    def root():
        return jsonify(
            service=service_version,
            color=service_color,
            host=socket.gethostname(),
        )

    @app.get("/info")
    def info():
        return jsonify(
            version=service_version,
            color=service_color,
            host=socket.gethostname(),
        )

    @app.route("/echo", methods=["GET", "POST"])
    def echo():
        return jsonify(
            method=request.method,
            version=service_version,
            headers={
                "X-Real-IP": request.headers.get("X-Real-IP"),
                "X-Forwarded-For": request.headers.get("X-Forwarded-For"),
                "X-Forwarded-Proto": request.headers.get("X-Forwarded-Proto"),
                "X-API-Version": request.headers.get("X-API-Version"),
            },
            args=request.args,
            json=request.get_json(silent=True),
        )

    @app.get("/health")
    def health():
        return jsonify(status="ok")

    return app


app = create_app()
