#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from requests_oauthlib import OAuth1Session
import psycopg2
import pandas as pd

def get_text(year, monthday, racenum):
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
    query = """
    SELECT
        t_predict.jyocd,
        COALESCE(t_name.bamei, '') AS bamei
    FROM t_predict
    LEFT JOIN t_name ON t_predict.kettonum = t_name.kettonum
    LEFT JOIN t_actual ON t_predict.year = t_actual.year
        AND t_predict.monthday = t_actual.monthday
        AND t_predict.jyocd = t_actual.jyocd
        AND t_predict.racenum = t_actual.racenum
        AND t_predict.kettonum = t_actual.kettonum
    LEFT JOIN t_umaban ON t_predict.year = t_umaban.year
        AND t_predict.monthday = t_umaban.monthday
        AND t_predict.jyocd = t_umaban.jyocd
        AND t_predict.racenum = t_umaban.racenum
        AND t_predict.kettonum = t_umaban.kettonum
    WHERE t_predict.year = '%s'
    AND t_predict.monthday = '%s'
    AND t_predict.racenum = '%s'
    ORDER BY predict;
    """
    with psycopg2.connect(dbparams) as conn:
        conn.set_client_encoding('UTF8')
        df = pd.io.sql.read_sql_query(query % (year, monthday, int(racenum)), conn)

    l_text = []
    for jyocd, grp in df.groupby('jyocd').__iter__():
        l_bamei = grp['bamei'].values
        l_text.append("%s %02dR\n ◎ %s\n ○ %s\n ▲%s\n 他のレースも http://tenmaai.info/ で見れます。\n" % (
            dic_jyo["%02d" % int(jyocd)],
            int(racenum),
            l_bamei[0],
            l_bamei[1],
            l_bamei[2]
        ))

    return l_text

# Consumer Key
CK = os.environ['CK']
# Consumer Secret
CS = os.environ['CS']
# Access Token
AT = os.environ['AT']
# Accesss Token Secert
AS = os.environ['AS']

# ツイート投稿用のURL
url = "https://api.twitter.com/1.1/statuses/update.json"

# ツイート本文
dbparams = "host={} user={} port={} password={} dbname={}".format(
    os.environ['DATABASE_HOST'],
    os.environ['DATABASE_USER'],
    os.environ['DATABASE_PORT'],
    os.environ['DATABASE_PASSWORD'],
    os.environ['DATABASE_NAME']
)

year = "2018"
monthday = "1124"
racenum = "09"
l_text = get_text(year, monthday, racenum)
for text in l_text:
    params = {"status": text}

    # OAuth認証で POST method で投稿
    twitter = OAuth1Session(CK, CS, AT, AS)
    req = twitter.post(url, params = params)

    # レスポンスを確認
    if req.status_code == 200:
        print ("OK")
    else:
        print ("Error: %d" % req.status_code)

