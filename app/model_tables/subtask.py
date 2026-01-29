# # app/model_tables/subtask.py
# from ..extensions import db

# class Subtask(db.Model):
#     __tablename__ = "subtasks"

#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(150), nullable=False)
#     is_completed = db.Column(db.Boolean, default=False, nullable=False)
#     task_id = db.Column(db.Integer, db.ForeignKey("task.id"), nullable=False)

#     def toggle(self):
#         self.is_completed = not self.is_completed
#         return self.is_completed

#     def to_dict(self):
#         return {
#             "id": self.id,
#             "title": self.title,
#             "is_completed": self.is_completed,
#             "task_id": self.task_id
#         }

#     def __repr__(self):
#         return f"<Subtask id={self.id} title={self.title} completed={self.is_completed}>"
