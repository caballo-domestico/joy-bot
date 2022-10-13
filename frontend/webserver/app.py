from flask import Flask, render_template, request, flash
import os
import boto3

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24).hex()
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