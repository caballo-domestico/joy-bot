from flask import Flask, render_template, request, url_for, flash, redirect, send_file
from werkzeug.utils import secure_filename
import boto3
from webserver.dao import PrescriptionsDao, PrescriptionBean
from tempfile import TemporaryFile
from urllib.parse import quote_plus
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config['SECRET_KEY'] = 'df0331cefc6c2b9a5d0208a726a5d1c0fd37324feba25509'
messages = [{'title': 'Message One',
             'content': 'Message One Content'},
            {'title': 'Message Two',
             'content': 'Message Two Content'}
            ]

@app.route('/', methods=('GET', 'POST'))
def index():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('analisi')

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        elif not content:
            flash('Content is required!')
        else:
            table.put_item(
            Item={
                    'cf': title,
                    'tipologia': content,
                }
            )
    return render_template('index.html')

ALLOWED_EXTENSIONS = {'txt', 'pdf'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload-prescription', methods=('GET', 'POST'))
def upload_prescription():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'prescription' not in request.files:
            flash('No prescription selected')
        file = request.files['prescription']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
        if file and allowed_file(file.filename):
            fileName = secure_filename(file.filename).replace(" ", "_")        
            username=quote_plus("test")
            dao = PrescriptionsDao()
            dao.storePrescription(prescriptionBean=PrescriptionBean(username=username, file=file, fileName=fileName))
            return redirect(f"/list-prescriptions?username={username}")
    return render_template('upload-prescription.html')

@app.route('/list-prescriptions', methods=['GET'])
def list_prescriptions():
    username = request.args.get('username', type=str)
    dao = PrescriptionsDao()
    names = dao.loadAllUserPrescriptionsNames(prescriptionBean=PrescriptionBean(username=username))
    return render_template('list-prescriptions.html', names=names, username=username)

@app.route('/get-prescription', methods=['GET'])
def get_prescription():
    dao = PrescriptionsDao()
    fileName = request.args.get('fileName', type=str)
    username = request.args.get('username', type=str)
    buf = TemporaryFile(mode="w+b")
    prescriptionBean = PrescriptionBean(username=username, file=buf, fileName=fileName)
    dao.loadPrescription(prescriptionBean=prescriptionBean)
    buf.seek(0)
    response = send_file(buf, attachment_filename=fileName, as_attachment=True)
    return response

        