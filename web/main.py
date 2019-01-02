# coding:utf-8
import urllib
from datetime import datetime
from flask import Flask, render_template, abort
import pandas as pd
from model import model
app = Flask(__name__)

@app.route("/")
def main():
    races_name, race_key = model.races()

    today = datetime.today()
    year = "%04d" % today.year
    monthday = "%02d%02d" % (today.month, today.day)
    races_name_today, race_key_today = model.races_day(year, monthday)

    return render_template('index.html',
        races=zip(races_name, race_key),
        races_today=zip(races_name_today, race_key_today))


def get_tweet_text(month, day, jyocd, racenum, prediction):
    dic_jyo = {
        '01': '札幌',
        '02': '函館',
        '03': '福島',
        '04': '新潟',
        '05': '東京',
        '06': '中山',
        '07': '中京',
        '08': '京都',
        '09': '阪神',
        '10': '小倉'
    }
    l_bamei = prediction['bamei'].values
    text = "%s月%s日%s%02dRレース予想\n" % (
        month,
        day,
        dic_jyo["%02d" % int(jyocd)],
        int(racenum)
    )
    for mark, bamei in zip(["◎", "○", "▲"], l_bamei[:3]):
        text += "%s %s" % (mark, bamei)
    return text

@app.route("/<raceid>")
def races(raceid):

    races_name, race_key = model.races()

    prediction = pd.DataFrame({
        "umaban": [],
        "bamei": [],
        "predict": [],
        "actual": [],
    })
    tweet_text = "TENMA"

    if len(raceid) == 12:
        try:
            year = raceid[:4]
            monthday = raceid[4:8]
            jyocd = raceid[8:10]
            racenum = raceid[10:12]
            app.logger.debug(year)
            app.logger.debug(monthday)
            app.logger.debug(jyocd)
            app.logger.debug(racenum)
            prediction = model.prediction(year, monthday, jyocd, racenum)

            if len(prediction.index) == 0:
                abort(404)


            tweet_text = get_tweet_text(monthday[:2], monthday[2:4], jyocd, racenum, prediction)
            tweet_text = urllib.parse.quote(tweet_text)

            return render_template('list.html',
                prediction=prediction,
                races=zip(races_name, race_key),
                now=raceid,
                tweet_text=tweet_text)
        except Exception as ex:
            app.logger.exception(ex)

    abort(404)

@app.errorhandler(404)
def page_not_found(error):
    msg = 'Error: {code} ページが見つかりません\n'.format(code=error.code)
    return msg, error.code


if __name__ == "__main__":
    # Only for debugging while developing
    app.run()
