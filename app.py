
from flask import Flask, render_template
import sqlite3
import os

app = Flask(__name__)

DATABASE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "smartcrop.db"
)


def get_sensor_data():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row

    try:
        latest = connection.execute("""
            SELECT *
            FROM sensor_records
            ORDER BY id DESC
            LIMIT 1
        """).fetchone()

        total = connection.execute("""
            SELECT COUNT(*) FROM sensor_records
        """).fetchone()[0]

        return latest, total

    finally:
        connection.close()


@app.route("/")
def home():
    latest, total = get_sensor_data()

    return render_template(
        "index.html",
        latest=latest,
        total=total
    )


if __name__ == "__main__":
    app.run(debug=True)
