# coding:utf-8
from flask import Flask, render_template
import pandas as pd
from model import model
app = Flask(__name__)

@app.route("/")
def main():
    races_name, race_key = model.races()
    return render_template('index.html',
        races=zip(races_name, race_key))


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
    return "%s月%s日%s%02dRレース予想\n◎ %s ○ %s ▲%s\n" % (
        month,
        day,
        dic_jyo["%02d" % int(jyocd)],
        int(racenum),
        l_bamei[0],
        l_bamei[1],
        l_bamei[2]
    )

@app.route("/<raceid>")
def races(raceid):

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
        tweet_text = get_tweet_text(monthday[:2], monthday[2:4], jyocd, racenum, prediction)
    else:
        prediction = pd.DataFrame({
            "umaban": [],
            "bamei": [],
            "predict": [],
            "actual": [],
        })
        tweet_text = "TENMA"

    return render_template('list.html',
        prediction=prediction,
        races=zip(races_name, race_key),
        now=raceid,
        tweet_text=tweet_text)


if __name__ == "__main__":
    # Only for debugging while developing
    app.run()
