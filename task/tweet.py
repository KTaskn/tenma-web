#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import datetime
from requests_oauthlib import OAuth1Session
import psycopg2
import pandas as pd
import numpy as np

def get_text(date, racenum):
    BIAS = 0.001
    query = """
    select
    t_keibajyo.name as keibajyo,
    t_race.course_id,
    t_race.kyori,
    t_horse.id AS horse_id,
    t_horse.name,
    t_tmp_horse.win / (select sum(1)::float from t_horserace where kakuteijyuni = 1) + {bias} as pab_horse,
    t_tmp_horse._count / (select sum(1)::float from t_horserace) + {bias} as pa_horse,
    case when t_tmp_course.win > 0 then t_tmp_sire.win / t_tmp_course.win::float + {bias} else {bias} end as pab_sire,
    case when t_tmp_course._count > 0 then t_tmp_sire._count / t_tmp_course._count::float + {bias} else {bias} end as pa_sire,
    t_tmp_broodmare.win / (select sum(1)::float from t_horserace where kakuteijyuni = 1)  + {bias} as pab_broodmare,
    t_tmp_broodmare._count / (select sum(1)::float from t_horserace) + {bias} as pa_broodmare,
    case when (select sum(1)::float from t_horserace where t_horserace.kakuteijyuni = 1 and t_horserace.racedate > DATE('{date}') - 30) > 0
        then t_tmp_kisyu.win / (select sum(1)::float from t_horserace where t_horserace.kakuteijyuni = 1 and t_horserace.racedate > DATE('{date}') - 30) + {bias}
        else {bias}
    end as pab_kisyu,
    case when (select sum(1)::float from t_horserace where t_horserace.racedate > DATE('{date}') - 30) > 0
        then t_tmp_kisyu._count / (select sum(1)::float from t_horserace where t_horserace.racedate > DATE('{date}') - 30) + {bias}
        else {bias}
    end as pa_kisyu
    from t_horserace
    inner join t_race on t_horserace.racedate = t_race.racedate
    and t_horserace.keibajyo_id = t_race.keibajyo_id
    and t_horserace.racenum = t_race.racenum
    inner join t_horse on t_horserace.horse_id = t_horse.id
    inner join t_keibajyo on t_horserace.keibajyo_id = t_keibajyo.id
    left join 
    (
    select
    t_horserace.horse_id,
    sum(case t_horserace.kakuteijyuni when 1 then 1 else 0 end) as win,
    sum(1) as _count
    from t_horserace
    group by t_horserace.horse_id
    ) as t_tmp_horse on t_tmp_horse.horse_id = t_horse.id
    left join 
    (
    select
    t_race.course_id,
    t_race.kyori,
    sum(case t_horserace.kakuteijyuni when 1 then 1 else 0 end) as win,
    sum(1) as _count
    from t_horserace
    inner join t_race on t_horserace.racedate = t_race.racedate
    and t_horserace.keibajyo_id = t_race.keibajyo_id
    and t_horserace.racenum = t_race.racenum
    group by t_race.course_id, t_race.kyori
    ) as t_tmp_course
    on t_tmp_course.course_id = t_race.course_id
    and t_tmp_course.kyori = t_race.kyori
    left join 
    (
    select
    t_race.course_id,
    t_race.kyori,
    t_horse.sire_id,
    sum(case t_horserace.kakuteijyuni when 1 then 1 else 0 end) as win,
    sum(1) as _count
    from t_horserace
    inner join t_horse on t_horserace.horse_id = t_horse.id
    inner join t_race on t_horserace.racedate = t_race.racedate
    and t_horserace.keibajyo_id = t_race.keibajyo_id
    and t_horserace.racenum = t_race.racenum
    group by t_race.course_id, t_race.kyori, sire_id
    ) as t_tmp_sire
    on t_tmp_sire.sire_id = t_horse.sire_id
    and t_tmp_sire.course_id = t_race.course_id
    and t_tmp_sire.kyori = t_race.kyori
    left join
    (
    select
    t_horse.broodmare_id,
    sum(case t_horserace.kakuteijyuni when 1 then 1 else 0 end) as win,
    sum(1) as _count
    from t_horserace
    inner join t_horse on t_horserace.horse_id = t_horse.id
    inner join t_race on t_horserace.racedate = t_race.racedate
    and t_horserace.keibajyo_id = t_race.keibajyo_id
    and t_horserace.racenum = t_race.racenum
    group by broodmare_id
    ) as t_tmp_broodmare
    on t_tmp_broodmare.broodmare_id = t_horse.broodmare_id
    left join
    (
    select
    t_horserace.kisyu_id,
    sum(case t_horserace.kakuteijyuni when 1 then 1 else 0 end) as win,
    sum(1) as _count
    from t_horserace
    where t_horserace.racedate > DATE('{date}') - 30
    group by t_horserace.kisyu_id
    ) as t_tmp_kisyu on t_tmp_kisyu.kisyu_id = t_horserace.kisyu_id
    where t_horserace.racedate = DATE('{date}')
    and t_horserace.racenum = {racenum};
    """
    with psycopg2.connect(dbparams) as conn:
        conn.set_client_encoding('UTF8')
        df = pd.io.sql.read_sql_query(query.format(date=date, racenum=racenum, bias=BIAS), conn)

    f_log = np.log
    if len(df.index) > 0:
        l_text = []
        for keibajyo, grp in df.groupby('keibajyo'):
            grp['pa'] = f_log(1 / 18.0)
            for col in ['horse', 'sire', 'broodmare', 'kisyu']:
                pa_col = "pa_%s" % col
                pab_col = "pab_%s" % col
                grp['pa'] = grp[pab_col].map(f_log) - grp[pa_col].map(f_log) + grp['pa']

            l_bamei = grp.sort_values('pa', ascending=False)['name'].values
            l_text.append("%s %02dR\n ◎ %s\n ○ %s\n ▲%s\n 他のレースも http://tenmaai.info/ で見れます。\n" % (
                keibajyo,
                int(racenum),
                l_bamei[0],
                l_bamei[1],
                l_bamei[2]
            ))

        return l_text
    return []

if __name__ == "__main__":
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
    dbparams = "host={} user={} port={} password={}".format(
        os.environ['DATABASE_HOST'],
        os.environ['DATABASE_USER'],
        os.environ['DATABASE_PORT'],
        os.environ['DATABASE_PASSWORD']
    )

    today = datetime.date.today()
    racenum = sys.argv[1]
    l_text = get_text(today, racenum)
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

