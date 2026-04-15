import os
import socket
import time

from flask import Flask, jsonify


def create_app() -> Flask:
    app = Flask(__name__)

    service_version = os.getenv("SERVICE_VERSION", "unknown")
    service_color = os.getenv("SERVICE_COLOR", "gray")
    slow_seconds = float(os.getenv("SLOW_SECONDS", "3"))

    @app.get("/")
    def root():
        time.sleep(slow_seconds)
        return jsonify(
            service=service_version,
            color=service_color,
            host=socket.gethostname(),
            slow_seconds=slow_seconds,
        )

    @app.get("/health")
    def health():
        return jsonify(status="ok")

    return app


app = create_app()
