from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/test")
def test_page():
    return "<p>This is test!</p>"

if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)
