# coding:utf-8
from flask import Flask, render_template
import model
app = Flask(__name__)

@app.route("/")
def main():
    prediction = model.prediction()
    app.logger.debug(prediction)
    return render_template('index.html', prediction=prediction)


if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=True, port=3000)