import json
from support import support_scripts


from flask import Flask, render_template, abort
from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, RadioField
from wtforms import validators


from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://postgres:123@localhost:5432/TeachersEnglish"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
app.secret_key = ('pgPhsrZR4DqDWHxV')

# -------------------------------ORM-------------------------------#
teachers_goals_assoc = db.Table('teachers_goals',
                                db.Column('teacher_id', db.Integer, db.ForeignKey('teachers.id'), primary_key=True),
                                db.Column('goal_id', db.Integer, db.ForeignKey('goals.id'), primary_key=True)
                                )


class Goal(db.Model):
    __tablename__ = 'goals'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    name_display = db.Column(db.String, nullable=False)
    teachers = db.relationship('Teacher', secondary=teachers_goals_assoc, back_populates='goals')
    requests = db.relationship('ClientRequests', back_populates='goal')


class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    about = db.Column(db.String)
    rating = db.Column(db.Float)
    picture = db.Column(db.String)
    price = db.Column(db.Integer)
    goals = db.relationship("Goal", secondary=teachers_goals_assoc, back_populates='teachers')
    free = db.Column(db.String)
    bookings = db.relationship("Booking", back_populates='teacher')

    def get_free(self):
        return json.loads(self.free)

    def get_info(self):
        info = {
            "id": self.id,
            "name": self.name,
            "about": self.about,
            "rating": self.rating,
            "picture": self.picture,
            "price": self.price,
            "goals": self.goals,
            "free": json.loads(self.free),
            "bookings": self.bookings
        }
        return info


class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    teacher = db.relationship('Teacher', uselist=False, back_populates='bookings')
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    day = db.Column(db.String, nullable=False)
    user_name = db.Column(db.String, nullable=False)
    user_phone = db.Column(db.String, nullable=False)
    start_time = db.Column(db.Text, nullable=False)


class ClientRequests(db.Model):
    __tablename__ = 'requests'
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String, nullable=False)
    user_phone = db.Column(db.String, nullable=False)
    goal_id = db.Column(db.Integer, db.ForeignKey('goals.id'))
    goal = db.relationship("Goal", uselist=False, back_populates='requests')
    time = db.Column(db.String, nullable=False)


# -------------------------------Forms-------------------------------#
class BookingForm(FlaskForm):
    name = StringField('Имя', [validators.InputRequired(message="Введите имя.")])
    phone = StringField('Телефон',
                        [validators.InputRequired(message='Введите номер.'), validators.Length(min=12, max=12)])
    clientWeekday = HiddenField('clientWeekday')
    clientTime = HiddenField('clientTime')
    clientTeacher = HiddenField('clientTeacher')


class RequestForm(FlaskForm):
    goals = RadioField('Какая цель занятий?', [validators.InputRequired(message='Выберете цель занятий')],
                       choices=[("travel", "Для путешествий"), ("study", "Для учебы"),
                                ("work", "Для работы"), ("relocate", "Для переезда"), ("prog", "Для программирования")])
    times = RadioField('Какая цель занятий?', [validators.InputRequired(message='Выберете время')],
                       choices=[("1", "1-2 часа в неделю"), ("3", "3-5 часов в неделю"),
                                ("2", "5-7 часов в неделю"), ("4", "7-10 часов в неделю")])
    name = StringField('Ваше имя', [validators.InputRequired(message='Введите имя'),
                                    validators.Length(min=1, max=25,
                                                      message='Имя должно содержать от 1 до 25 символов')])
    phone = StringField('Ваш телефон',
                        [validators.InputRequired(message='Введите номер'), validators.Length(min=12, max=12)])


# -------------------------------Routes-------------------------------#
@app.route('/')
def main():
    teachers_data = Teacher.query.order_by(db.func.random()).limit(6).all()
    return render_template('index.html', teachers=teachers_data)


@app.route('/all_teachers/')
def all_teachers():
    teachers_data = Teacher.query.order_by(Teacher.rating.desc()).all()
    return render_template('all_teachers.html', teachers_data=teachers_data)


@app.route('/goals/<goal>/')
def goals(goal):
    teachers_data = Teacher.query.order_by(Teacher.rating.desc()).all()
    goal = Goal.query.filter(Goal.name == goal).first()
    return render_template('goal.html', teachers_data=teachers_data, goal=goal)


@app.route('/profiles/<int:id>/')
def profile(id):
    try:
        teachers_data = Teacher.query.get(id)
        return render_template('profile.html', teacher=teachers_data)
    except:
        abort(404)


@app.route('/request/')
def request():
    form = RequestForm()
    return render_template('request.html', form=form)


@app.route('/request_done/', methods=["GET", "POST"])
def request_done():
    form = RequestForm()
    goal = Goal.query.filter(Goal.name == form.goals.data).first()
    time = form.times.data
    name = form.name.data
    phone = form.phone.data
    if form.validate_on_submit():
        client = ClientRequests(user_name=name, user_phone=phone, goal=goal, time=time)
        db.session.add(client)
        db.session.commit()
        return render_template('request_done.html', goal=goal, time=time, name=name, phone=phone)
    return render_template('request.html', form=form)


@app.route('/booking/<int:id>/<week>/<time>/')
def booking(id, week, time):
    booking_form = BookingForm()
    path = f'/booking/{str(id)}/{week}/{time}/'
    try:
        teachers_data = Teacher.query.get(id)
        support_scripts.booking_link_checker(path=path, teacher=teachers_data)  # Проверяет корректность URL
        return render_template('booking.html', form=booking_form, week=week, time=time,
                               teacher=teachers_data)
    except:
        abort(404)


@app.route('/booking_done/', methods=["GET", "POST"])
def booking_done():
    booking_form = BookingForm()
    name = booking_form.name.data
    phone = booking_form.phone.data
    weekDay = booking_form.clientWeekday.data
    time = booking_form.clientTime.data
    teach_id = int(booking_form.clientTeacher.data)
    teacher = Teacher.query.get(teach_id)

    if booking_form.validate_on_submit():
        client = Booking(teacher=teacher, day=weekDay, user_name=name, user_phone=phone, start_time=time)
        db.session.add(client)
        db.session.commit()
        return render_template('booking_done.html', name=name, phone=phone, weekDay=weekDay, time=time)
    return render_template('booking.html', form=booking_form, id=teach_id, week=weekDay, time=time,
                           teachers=teacher)


@app.route('/about/')
def about():
    return render_template('about.html')


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', title='404', error=error), 404


if __name__ == '__main__':
    app.run()
