from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/result')
def result():
    list = [("1", 'https://google.com/'), ("2", 'https://google.com/'), ("3", 'https://google.com/'), ("4", 'https://google.com/')]
    return render_template('result.html', keyword=request.args['keyword'], list=list)
