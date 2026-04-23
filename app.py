from typing import Dict, Union

from flask import Flask

from app import create_app, load_settings

settings: Dict[str, Union[bool, str, int]] = load_settings()

host: str = settings["host"]
port: int = settings["port"]
debug: bool = settings["debug"]

app: Flask = create_app()


if __name__ == "__main__":
    app.run(host=host, port=port, debug=debug, threaded=True)
