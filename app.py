import os
import flask
import pickle
import sys, fitz
from flask import Flask, request, url_for, render_template, send_from_directory
from itertools import *
import time
import random

import spacy

UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/uploads/'

model_path = 'model/model_2'
model = spacy.load(model_path)

app = Flask(__name__, static_url_path="/static")
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/uploads/<filename>')
def uploaded_file(filename):
   return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        f = request.files.getlist('files')
        result = []

        for file in f:
            if file:
                filename = file.filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                doc = fitz.open(upload_dir)
                text = ""
                for page in doc:
                    text = text + str(page.getText())
                
                tx = "".join(text.split('\n'))
                doc = model(tx)
                # entities = {key: list(g) for key, g in groupby(sorted(doc.ents, key=lambda x: x.label_), lambda x: x.label_)}
                entities = {key: list(set(map(lambda x: str(x), g))) for key, g in groupby(sorted(doc.ents, key=lambda x: x.label_), lambda x: x.label_)}

                result.append(entities)

        return render_template('result.html', result=result)

    return render_template('index.html')

if __name__ == '__main__':
    app.run()
