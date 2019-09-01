# coding:utf-8
import urllib
from datetime import date
from flask import Flask, render_template, abort, Markup, make_response, jsonify, request
import pandas as pd
import numpy as np
from model import model
app = Flask(__name__)

@app.route("/")
def main():
    today = date.today()
    races_name_today, race_key_today = model.races_day(today)

    return render_template('index.html', races_today=zip(races_name_today, race_key_today))


def get_tweet_text(prediction_table, date, keibajyo, racenum):
    l_bamei = prediction_table['name'].values
    date_str = str(date)
    date = "%s年%s月%s日" % (date_str[:4], date_str[4:6], date_str[6:8])
    text = "%s %s %02dRレース予想\n" % (date_str, keibajyo, racenum)
    for mark, bamei in zip(["◎", "○", "▲"], l_bamei[:3]):
        text += "%s %s" % (mark, bamei)
    return text

@app.route("/<raceid>")
def races(raceid):
    if len(raceid) == 12:
        try:
            date = int(raceid[:8])
        except ValueError:
            abort(404)
            
        try:
            keibajyo_id = int(raceid[8:10])
        except ValueError:
            abort(404)

        try:
            racenum = int(raceid[10:12])
        except ValueError:
            abort(404)

        df_prediction = model.prediction(date, keibajyo_id, racenum)


        if len(df_prediction.index) < 1:
            abort(404)
            
        tweet_text = get_tweet_text(df_prediction, date, df_prediction.ix[0, 'keibajyo'], racenum)

    else:
        abort(404)

    return render_template('list.html',
        df_prediction=df_prediction,
        tweet_text=tweet_text
    )

@app.route("/sitemap.xml", methods=['GET'])
def sitemap():

    l_races = model.races()

    sitemap_xml = render_template('sitemap.xml',
        races=l_races
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
    date = request.args.get('date')

    try:
        keibajyo = model.keibajyo(int(date))
    except ValueError:
        keibajyo = []
    return jsonify(keibajyo)

@app.route("/get_race", methods=['GET'])
def get_race():
    date = request.args.get('date')
    keibajyo_id = request.args.get('keibajyo_id')
    try :
        racenum = model.racenum(int(date), int(keibajyo_id))
        return jsonify(racenum)
    except ValueError:
        return jsonify([])


@app.route("/get_hist", methods=['GET'])
def get_titiuma():
    date = request.args.get('date')
    keibajyo_id = request.args.get('keibajyo_id')
    racenum = request.args.get('racenum')
    horse_id = request.args.get('horse_id')
    
    try:
        return jsonify(
            model.get_hist(
                int(date), int(keibajyo_id), int(racenum), int(horse_id)
            )
        )
    except ValueError:
        return jsonify([])


@app.errorhandler(404)
def page_not_found(error):
    msg = 'Error: {code} ページが見つかりません\n'.format(code=error.code)
    return msg, error.code


if __name__ == "__main__":
    # Only for debugging while developing
    app.run()
