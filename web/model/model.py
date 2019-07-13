# coding: utf-8
import os
import psycopg2
import pandas as pd

dbparams = "host={} user={} port={} password={}".format(
    os.environ['DATABASE_HOST'],
    os.environ['DATABASE_USER'],
    os.environ['DATABASE_PORT'],
    os.environ['DATABASE_PASSWORD']
)

def races():
    query = """
    SELECT
    TO_CHAR(t_race.racedate, 'yyyy-mm-dd') AS racedate,
    t_keibajyo.name AS keibajyo_name,
    t_race.racenum
    FROM t_race
    INNER JOIN t_keibajyo ON t_race.keibajyo_id = t_keibajyo.id
    WHERE t_race.racedate >= DATE('2019-01-01')
    ORDER BY racedate DESC, t_race.keibajyo_id ASC, t_race.racenum ASC;
    """
    with psycopg2.connect(dbparams) as conn:
        conn.set_client_encoding('UTF8')
        df = pd.io.sql.read_sql_query(query, conn)
    l_text = []
    l_key = []
    for racedate, keibajyo_name, racenum in df.values:
        l_text.append("%s %sR %s" % (racedate, racenum, keibajyo_name))
        l_key.append("%s%s%s" % (racedate, racenum, keibajyo_name))
    return l_text, l_key

def races_day(date):
    query = """
    SELECT
    TO_CHAR(t_race.racedate, 'yyyy-mm-dd') AS racedate,
    t_keibajyo.name AS keibajyo_name,
    t_race.racenum
    FROM t_race
    INNER JOIN t_keibajyo ON t_race.keibajyo_id = t_keibajyo.id
    WHERE t_race.racedate = DATE('%s')
    ORDER BY racedate DESC, t_race.keibajyo_id ASC, t_race.racenum ASC;
    """

    with psycopg2.connect(dbparams) as conn:
        conn.set_client_encoding('UTF8')
        df = pd.io.sql.read_sql_query(query % (date), conn)
    l_text = []
    l_key = []
    for racedate, keibajyo_name, racenum in df.values:
        l_text.append("%s %s %sR" % (racedate, keibajyo_name, racenum))
        l_key.append("%s%s%s" % (racedate, racenum, keibajyo_name))
    return l_text, l_key

def racedays():
    query = """
    SELECT
    DISTINCT TO_CHAR(t_race.racedate, 'yyyy-mm-dd') AS racedate
    FROM t_race
    ORDER BY racedate DESC LIMIT 12;
    """

    with psycopg2.connect(dbparams) as conn:
        conn.set_client_encoding('UTF8')
        df = pd.io.sql.read_sql_query(query, conn)
        
    return df['racedate'].values.tolist()

def keibajyo(date):
    query = """
    SELECT
    DISTINCT
    t_race.keibajyo_id AS keibajyo_id,
    t_keibajyo.name AS keibajyo_name
    FROM t_race
    INNER JOIN t_keibajyo ON t_race.keibajyo_id = t_keibajyo.id
    WHERE t_race.racedate = DATE('%s')
    ORDER BY t_race.keibajyo_id ASC;
    """

    with psycopg2.connect(dbparams) as conn:
        conn.set_client_encoding('UTF8')
        df = pd.io.sql.read_sql_query(query % (date), conn)

    return dict(zip(
        df['keibajyo_id'].values.tolist(),
        df['keibajyo_name'].values.tolist()
    ))

def racenum(date, keibajyo_id):
    query = """
    SELECT
    DISTINCT t_race.racenum
    FROM t_race
    WHERE t_race.racedate = DATE('%s') AND t_race.keibajyo_id = %s
    ORDER BY t_race.racenum ASC;
    """

    with psycopg2.connect(dbparams) as conn:
        conn.set_client_encoding('UTF8')
        df = pd.io.sql.read_sql_query(query % (date, keibajyo_id), conn)
    
    return df['racenum'].values.tolist()

def prediction(year, monthday, jyocd, racenum):
    query = """
    SELECT
        COALESCE(t_umaban.umaban, '') AS umaban,
        COALESCE(t_name.bamei, '') AS bamei,
        COALESCE(t_predict.predict::text, '')::int AS predict,
        COALESCE(t_odds.odds::text, '') AS odds,
        COALESCE(t_actual.actual::text, '') AS actual
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
    LEFT JOIN t_odds ON t_predict.year = t_odds.year
        AND t_predict.monthday = t_odds.monthday
        AND t_predict.jyocd = t_odds.jyocd
        AND t_predict.racenum = t_odds.racenum
        AND t_predict.kettonum = t_odds.kettonum
    WHERE t_predict.year = '%s'
    AND t_predict.monthday = '%s'
    AND t_predict.jyocd = '%s'
    AND t_predict.racenum = '%s'
    ORDER BY predict;
    """
    with psycopg2.connect(dbparams) as conn:
        conn.set_client_encoding('UTF8')
        return pd.io.sql.read_sql_query(query % (year, monthday, int(jyocd), int(racenum)), conn)

def prediction_umatan(year, monthday, jyocd, racenum, num=10):
    query = """
    SELECT
        COALESCE(t_name_1.bamei, '') AS bamei_1,
        COALESCE(t_name_2.bamei, '') AS bamei_2,
        COALESCE(t_umatan.odds::text, '')::float AS odds
    FROM t_umatan
    LEFT JOIN t_name AS t_name_1 ON t_umatan.kettonum_1chaku = t_name_1.kettonum
    LEFT JOIN t_name AS t_name_2 ON t_umatan.kettonum_2chaku = t_name_2.kettonum
    WHERE t_umatan.year = '%s'
    AND t_umatan.monthday = '%s'
    AND t_umatan.jyocd = '%s'
    AND t_umatan.racenum = '%s'
    ORDER BY odds LIMIT %d;
    """
    with psycopg2.connect(dbparams) as conn:
        conn.set_client_encoding('UTF8')
        return pd.io.sql.read_sql_query(query % (year, monthday, int(jyocd), int(racenum), int(num)), conn)


def get_factor_text(score):
    if score > 0.5:
        return "◎%sがとてもよい"
    elif score > 0.0:
        return "○%sがよい"
    elif score > -0.5:
        return "▲%sが注意"
    else:
        return "×%sが不安要素"

def prediction_factor(year, monthday, jyocd, racenum):
    query = """
    SELECT
        COALESCE(t_name.bamei, '') AS bamei,
        t_factor.factor,
        t_factor.score
    FROM t_factor
    LEFT JOIN t_name AS t_name ON t_factor.kettonum = t_name.kettonum
    LEFT JOIN t_predict ON t_factor.year = t_predict.year
        AND t_factor.monthday = t_predict.monthday
        AND t_factor.jyocd = t_predict.jyocd
        AND t_factor.racenum = t_predict.racenum
        AND t_factor.kettonum = t_predict.kettonum
    WHERE t_factor.year = '%s'
    AND t_factor.monthday = '%s'
    AND t_factor.jyocd = '%s'
    AND t_factor.racenum = '%s'
    ORDER BY t_predict.predict ASC, t_factor.score DESC;
    """
    with psycopg2.connect(dbparams) as conn:
        conn.set_client_encoding('UTF8')
        df = pd.io.sql.read_sql_query(query % (year, monthday, int(jyocd), int(racenum)), conn)

    l_factor_detail = []
    dic_factor = {
        "kisyucode": "騎手",
        "ketto3infohansyokunum1": "父馬",
        "kakuteijyuni_bf1": "１走前",
        "kakuteijyuni_bf2": "２走前",
        "kakuteijyuni_bf3": "３走前",
        "kakuteijyuni_bf4": "４走前",
    }

    l_idx = []
    l_name = []
    l_factor_detail = []
    for bamei, grp in df.groupby('bamei'):
        text = ""
        for idx, row in grp[['score', 'factor']].iterrows():
            if text:
                text += "<br />"
            text += "%s" % (
                get_factor_text(row['score']) % dic_factor[row['factor']]
            )
        l_idx.append(idx)
        l_name.append(bamei)
        l_factor_detail.append(text)

    return pd.DataFrame({
        "idx": l_idx,
        "bamei": l_name,
        "factor_detail": l_factor_detail
    }).sort_values('idx')

def get_racename(year, monthday, jyocd, racenum):
    query = """
    SELECT
        COALESCE(t_racename.racename, '') AS racename
    FROM t_racename
    WHERE t_racename.year = '%s'
    AND t_racename.monthday = '%s'
    AND t_racename.jyocd = '%s'
    AND t_racename.racenum = '%s' LIMIT 1;
    """
    with psycopg2.connect(dbparams) as conn:
        conn.set_client_encoding('UTF8')
        df = pd.io.sql.read_sql_query(query % (year, monthday, int(jyocd), int(racenum)), conn)

    if len(df.values):
        return df['racename'].values[0]
    else:
        return ""

def get_hist_titiuma(code):
    query = """
    SELECT
    kakuteijyuni,
    _count,
    FROM t_titiuma_jyuni
    WHERE t_titiuma_jyuni.code = '%s'
    AND t_titiuma_jyuni.jyocd = '%s'
    AND t_titiuma_jyuni.kyori = '%s'
    AND t_titiuma_jyuni.course = '%s'
    AND t_titiuma_jyuni.
    """