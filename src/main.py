from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/test")
def hello_world():
    return "<p>This is test!</p>"

if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)
