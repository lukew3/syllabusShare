from flask import Flask, render_template, request, send_from_directory, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024 # 10 MB
db = SQLAlchemy(app)
upload_path = os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'])
if not os.path.isdir(upload_path):
    os.makedirs(upload_path)

class School(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    courses = db.relationship('Course', backref='school', lazy=True)

    def __repr__(self):
        return f"School('{self.name}', '{self.courses}')"

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    syllabi = db.relationship('Syllabus', backref='course', lazy=True)

    def __repr__(self):
        return f"Course('{self.name}', '{self.school_id}')"

class Syllabus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    instructor = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

    def __repr__(self):
        return f"Course('{self.instructor}', '{self.year}')"

db.create_all()

def generate_filename(school, course, instructor, year):
    school = school.replace(' ', '+')
    course = course.replace(' ', '+')
    instructor = instructor.replace(' ', '+')
    return f"{course}_{school}_{instructor}_{year}.pdf"

@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        return render_template('upload_form.html')
    elif request.method == 'POST':
        print(request.files)
        f = request.files['attachment']
        print(f.filename)
        # should ensure file is pdf here
        filename = generate_filename(request.form['school'], request.form['course'], request.form['instructor'], request.form['year'])
        f.save(os.path.join(upload_path, filename))
        schoolname = request.form['school']
        school = School.query.filter_by(name=schoolname).first()
        course = None
        if not school:
            new_school = School(name=schoolname)
            db.session.add(new_school)
            db.session.commit()
            school = new_school
        else:
            course = Course.query.filter_by(school_id=school.id, name=request.form['course']).first()
        if not course:
            new_course = Course(school_id=school.id, name=request.form['course'])
            db.session.add(new_course)
            db.session.commit()
            course = new_course
        duplicate = Syllabus.query.filter_by(instructor=request.form['instructor'], year=int(request.form['year']), course_id=course.id).first()
        if not duplicate:
            new_syllabi = Syllabus(
                instructor=request.form['instructor'],
                year=int(request.form['year']),
                course_id=course.id
            )
            db.session.add(new_syllabi)
            db.session.commit()
        return redirect(url_for('upload'))

@app.route('/download/<filename>')
def download_file(filename=None):
    if not filename:
        return 404
    return send_from_directory(directory=upload_path, path=filename)

@app.route("/")
def home():
    schools = School.query.order_by(School.name.asc()).all()
    return render_template('home.html', schools=schools)

@app.route("/getCourses/<school_name>")
def get_courses(school_name=None):
    school_name = school_name.replace('+', ' ')
    school = School.query.filter_by(name=school_name).first()
    courses = Course.query.filter_by(school_id=school.id).order_by(Course.name.asc()).all()
    courses_json_ready = []
    for course in courses:
        courses_json_ready.append({"id": course.id, "name": course.name})
    return jsonify(courses_json_ready)

@app.route("/schools")
def schools():
    schools = School.query.order_by(School.name.asc()).all()
    return render_template('schools.html', schools=schools)


@app.route("/<school_name_safe>")
def school_courses(school_name_safe=None):
    school_name = school_name_safe.replace('+', ' ')
    school = School.query.filter_by(name=school_name).first()
    if not school:
        return '<p>Not found</p>'
    courses = Course.query.filter_by(school_id=school.id).order_by(Course.name.asc()).all()
    return render_template('school_courses.html', school_name=school.name, school_name_safe=school_name_safe, courses=courses)

@app.route("/<school_name_safe>/<course_name_safe>")
def course_syllabi(school_name_safe=None, course_name_safe=None):
    school_name = school_name_safe.replace('+', ' ')
    course_name = course_name_safe.replace('+', ' ')
    course = Course.query.filter_by(name=course_name).first()
    syllabi = Syllabus.query.filter_by(course_id=course.id).order_by(Syllabus.instructor.asc()).order_by(Syllabus.year.asc()).all()
    return render_template('course_syllabi.html', school_name=school_name, course_name=course.name, syllabi=syllabi)

if __name__ == '__main__':
    app.run(debug=True)
