import os
from flask import Flask
from database import init_db
from routes import register_routes

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "resultms_secret_2026")

init_db()
register_routes(app)

if __name__ == "__main__":
    print("=" * 50)
    print("  Result Management System Running")
    print("  Open: http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=True)