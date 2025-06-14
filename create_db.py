from app import create_app
from app.models import db, Task, Subtask

# Create the Flask app using your factory
app = create_app()

# Run database setup in the app context
with app.app_context():
    db.create_all()
    print("Database tables created.")

    # Optional: Add sample data only if no tasks exist
    if Task.query.count() == 0:
        task = Task(title="Build To-Do App", description="Build and test the to-do app.")
        subtask1 = Subtask(title="Create models", task=task)
        subtask2 = Subtask(title="Set up CRUD", task=task)

        db.session.add(task)
        db.session.add_all([subtask1, subtask2])
        db.session.commit()
        print("Sample data inserted.")