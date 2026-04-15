import os
import socket

from flask import Flask, jsonify


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

    @app.get("/health")
    def health():
        return jsonify(status="ok")

    return app


app = create_app()
