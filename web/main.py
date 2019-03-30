# coding:utf-8
import urllib
from datetime import datetime
from flask import Flask, render_template, abort, Markup, make_response, jsonify, request
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
            prediction_umatan = model.prediction_umatan(year, monthday, jyocd, racenum, num=8)
            prediction_factor = model.prediction_factor(year, monthday, jyocd, racenum)
            prediction_factor['factor_detail'] = prediction_factor['factor_detail'].map(Markup)
            umatan_flg = (len(prediction_umatan.index) > 0)
            factor_flg = (len(prediction_factor.index) > 0)
            racename = model.get_racename(year, monthday, jyocd, racenum)

            if len(prediction.index) == 0:
                abort(404)


            tweet_text = get_tweet_text(monthday[:2], monthday[2:4], jyocd, racenum, prediction)
            tweet_text = urllib.parse.quote(tweet_text)

            return render_template('list.html',
                prediction=prediction,
                umatan_flg=umatan_flg,
                factor_flg=factor_flg,
                prediction_umatan=prediction_umatan,
                prediction_factor=prediction_factor,
                races=zip(races_name, race_key),
                now=raceid,
                tweet_text=tweet_text,
                racename=racename)
        except Exception as ex:
            app.logger.exception(ex)

    abort(404)

@app.route("/sitemap.xml", methods=['GET'])
def sitemap():

    races_name, race_key = model.races()

    prediction = pd.DataFrame({
        "umaban": [],
        "bamei": [],
        "predict": [],
        "actual": [],
    })

    sitemap_xml = render_template('sitemap.xml',
        races=race_key
    )
    response = make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"
    return response

@app.route("/get_racedays", methods=['GET'])
def get_raceday():
    racedays = model.racedays()
    return jsonify(racedays)

@app.route("/get_keibajyo", methods=['GET'])
def get_keibajyo():
    yearmonthday = request.args.get('yearmonthday')
    if len(yearmonthday) == 8:
        year = yearmonthday[:4]
        monthday = yearmonthday[4:]
        keibajyo = model.keibajyo(year, monthday)
        return jsonify(keibajyo)
    else:
        return jsonify([])

@app.route("/get_race", methods=['GET'])
def get_race():
    yearmonthday = request.args.get('yearmonthday')
    jyocd = request.args.get('jyocd')
    l = list(map(lambda i: "%02d" % (i), range(10)))

    app.logger.info(l)
    if len(yearmonthday) == 8 and jyocd in l:
        year = yearmonthday[:4]
        monthday = yearmonthday[4:]

        racenum = model.racenum(year, monthday, int(jyocd))
        return jsonify(racenum)
    else:
        return jsonify([])


@app.errorhandler(404)
def page_not_found(error):
    msg = 'Error: {code} ページが見つかりません\n'.format(code=error.code)
    return msg, error.code


if __name__ == "__main__":
    # Only for debugging while developing
    app.run()
