import os
from flask import Flask, flash, request, render_template, redirect, url_for, send_from_directory
from livereload import Server, shell
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['pdf'])

# Basic Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# remember to use DEBUG mode for templates auto reload
# https://github.com/lepture/python-livereload/issues/144
app.debug = True

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Flask route
@app.route('/')
def index():
    return render_template('welcome.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Check if post request has the file part.
        if 'store_file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['store_file']
        # If user does not select file, browse also
        # Submit an empty part without filename
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Change file permissions.
            os.chmod(os.path.join(app.config['UPLOAD_FOLDER']) + '/' + filename, 0o775)
            return redirect('documents')
    return render_template('upload-form.html')

@app.route('/documents')
def documents():
    file_dir = 'uploads'
    files_list = {}
    for filename in os.listdir(file_dir):
        files_list[filename] = 'https://' + request.host + '/uploads/' + filename
    return render_template('doc-list.html', files=files_list)

@app.route('/' + UPLOAD_FOLDER + '/<file>')
def file_show(file = None):
    return send_from_directory(UPLOAD_FOLDER, file)

# Live reload server
# Prob want to set some sort of env flag to only do this on DEV
server = Server(app.wsgi_app)

# use custom host and port
server.serve(port=80, host='0.0.0.0')
