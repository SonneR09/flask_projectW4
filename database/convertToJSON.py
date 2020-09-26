"""Converting data.py file into .JSON format"""
import json
from database import data

data_teachers = json.dumps(data.teachers)
data_goals = json.dumps(data.goals)

with open('teachers_data.json', 'w') as f:
    f.write(data_teachers)

with open('goals_data.json', 'w') as f:
    f.write(data_goals)
