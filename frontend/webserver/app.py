from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.utils import secure_filename
import boto3
from os import environ

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
            filename = secure_filename(file.filename)            
            # TODO: upload file to dynamo db
            dynamodb = boto3.resource('dynamodb')
            client = boto3.client('dynamodb')
            table = dynamodb.Table('Prescriptions')
            # TODO: update username and s3url with real values
            username="test"
            s3Url = "test"
            table.put_item(
                Item={
                    "id": f"{username}_{filename}",
                    "username": f"{username}",
                    "prescription": f"{s3Url}"
                }
            )
            response = table.scan()
            items = response['Items']
            flash(f"uploaded file: {filename}")
            flash(f"items: {items}")
            return redirect(request.url)


    return render_template('upload-prescription.html')