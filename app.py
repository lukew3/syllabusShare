from flask import Flask, render_template, request
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
upload_path = os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'])


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

@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        return render_template('upload_form.html')
    elif request.method == 'POST':
        f = request.files['the_file']
        filename = "example.pdf"
        f.save(path + filename)

@app.route('/s/<school>/<course>/<filename>')
def download_file(filename=None):
    if not filename:
        return 404
    # check for file in directory first?
    return send_from_directory(directory=upload_path, filename=filename)


if __name__ == '__main__':
    app.run(debug=True)
