from flask import Flask, render_template, request
from web_agent import search
app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/result')
def result():
    res = search(request.args['keyword'])
    return render_template('result.html', keyword=request.args['keyword'], list=res)
