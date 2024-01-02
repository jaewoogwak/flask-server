from flask import Flask, jsonify

app = Flask(__name__)

address = ''


@app.route('/')
def hello():
    return jsonify(message='Hello, this is Flask server!')


if __name__ == '__main__':
    app.run(debug=True, host=address, port=5000)
