from flask import Flask

app = Flask(__name__)

@app.route('/test')
def test():
    return 'Flask is working!'

if __name__ == '__main__':
    app.run(debug=True, port=5000)
