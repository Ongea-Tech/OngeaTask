from app import create_app, db

app = create_app()

with app.app_context():
    db.session.execute(db.text("SET FOREIGN_KEY_CHECKS=0;"))
    db.drop_all()
    db.session.execute(db.text("SET FOREIGN_KEY_CHECKS=1;"))
    db.create_all()
    print("Database reset successfully.")

