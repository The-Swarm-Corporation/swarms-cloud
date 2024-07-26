from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/send", methods=["POST"])
def send():
    data = request.get_json()
    return jsonify(data)


if __name__ == "__main__":
    app.run(port=5000)
