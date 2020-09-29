import json

from database import data
from app import Teacher, db, Goal


def fill_db():
    goals = {}
    for goal_name, goal_display in data.goals.items():
        db_goal = Goal(name=goal_name, name_display=goal_display)
        db.session.add(db_goal)
        goals[goal_name] = db_goal
    for teacher in data.teachers:
        teacher_fill = Teacher(
            name=teacher['name'],
            about=teacher['about'],
            rating=teacher['rating'],
            picture=teacher['picture'],
            price=teacher['price'],
            free=json.dumps(teacher['free']),
        )
        for teach_goal_name in teacher['goals']:
            teacher_fill.goals.append(goals[teach_goal_name])
        db.session.add(teacher_fill)

    db.session.commit()


if __name__ == '__main__':
    fill_db()
