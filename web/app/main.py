# coding:utf-8
from flask import Flask, render_template
import pandas as pd
import model
app = Flask(__name__)

@app.route("/<raceid>")
def main(raceid):
    races_name, race_key = model.races()
    if len(raceid) == 12:
        year = raceid[:4]
        monthday = raceid[4:8]
        jyocd = raceid[8:10]
        racenum = raceid[10:12]
        app.logger.debug(year)
        app.logger.debug(monthday)
        app.logger.debug(jyocd)
        app.logger.debug(racenum)
        prediction = model.prediction(year, monthday, jyocd, racenum)
    else:
        prediction = pd.DataFrame({
            "umaban": [],
            "bamei": [],
            "predict": [],
            "actual": [],
        })
    return render_template('index.html',
        prediction=prediction,
        races=zip(races_name, race_key))


if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=True, port=3000)