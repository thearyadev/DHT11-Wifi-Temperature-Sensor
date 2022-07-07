from flask import Flask, render_template, request, Response

app = Flask(__name__, static_folder='static', static_url_path='')


@app.route('/')
def index():
    return render_template("index.html")


@app.route("/ce")
def correct_endpoint():
    return Response("Correct endpoint", status=200)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
