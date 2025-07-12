from app import create_app, db
from app.models import Task, Subtask

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()
    print("Database reset successfully.")

