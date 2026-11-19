"""Arranca el servidor de desarrollo:  python run.py   ->  http://127.0.0.1:5000"""
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
