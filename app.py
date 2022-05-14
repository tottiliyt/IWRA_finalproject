from flask import Flask, render_template, request
from web_agent import search

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/result')
def result():
    df = search(request.args['keyword'], request.args['option'])
    return render_template(
        'result.html', 
        keyword=request.args['keyword'], 
        option=request.args['option'],
        result=df.to_numpy())

if __name__ == '__main__':
    app.run(threaded=True, port=5000)
