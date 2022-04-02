from flask import Flask
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
upload_path = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])


@app.route("/")
def home():
    return render_template('home.html')

@app.route("/s")
def schools():
    return render_template('schools.html')

@app.route("/s/<school>")
def school_courses(school=None):
    return render_template('school_courses.html')

@app.route("/s/<school>/<course>")
def course_syllabi(school=None, course=None):
    return render_template('course_syllabi.html')

@app.route("/upload", methods=['GET'])
def upload_form():
    return render_template('upload_form.html')

@app.route("/submit", methods=['POST'])
def submit_form():
    return "<p>Success</p>"

@app.route('/s/<school>/<course>/<filename>')
def download_file(filename=None):
    if not filename:
        return 404
    # check for file in directory first?
    return send_from_directory(directory=upload_path, filename=filename)

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['the_file']
        filename = "example.pdf"
        f.save(path + filename)
