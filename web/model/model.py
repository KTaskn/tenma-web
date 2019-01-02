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
        COALESCE(t_predict.year::text, '') AS yaer,
        LPAD(COALESCE(t_predict.monthday::text, ''), 4, '0') AS monthday,
        LPAD(COALESCE(t_predict.jyocd::text, ''), 2, '0') AS jyocd,
        LPAD(COALESCE(t_predict.racenum::text, ''), 2, '0') AS racenum
    FROM t_predict
    GROUP BY year, monthday, jyocd, racenum
    ORDER BY year DESC, monthday DESC, jyocd, racenum;
    """
    with psycopg2.connect(dbparams) as conn:
        conn.set_client_encoding('UTF8')
        df = pd.io.sql.read_sql_query(query, conn)
    l_text = []
    l_key = []
    for year, monthday, jyocd, racenum in df.values:
        l_text.append("%s-%s-%s %s %sR" % (year, monthday[:2], monthday[2:4], dic_jyo[jyocd], racenum))
        l_key.append("%s%s%s%s%s" % (year, monthday[:2], monthday[2:4], jyocd, racenum))
    return l_text, l_key

def races_day(year, monthday):
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
        COALESCE(t_predict.year::text, '') AS yaer,
        LPAD(COALESCE(t_predict.monthday::text, ''), 4, '0') AS monthday,
        LPAD(COALESCE(t_predict.jyocd::text, ''), 2, '0') AS jyocd,
        LPAD(COALESCE(t_predict.racenum::text, ''), 2, '0') AS racenum
    FROM t_predict
    WHERE t_predict.year = '%s'
    AND t_predict.monthday = '%s'
    GROUP BY year, monthday, jyocd, racenum
    ORDER BY year DESC, monthday DESC, jyocd, racenum;
    """

    with psycopg2.connect(dbparams) as conn:
        conn.set_client_encoding('UTF8')
        df = pd.io.sql.read_sql_query(query % (year, monthday), conn)
    l_text = []
    l_key = []
    for year, monthday, jyocd, racenum in df.values:
        l_text.append("%s %sR" % (dic_jyo[jyocd], racenum))
        l_key.append("%s%s%s%s%s" % (year, monthday[:2], monthday[2:4], jyocd, racenum))
    return l_text, l_key



def prediction(year, monthday, jyocd, racenum):
    query = """
    SELECT
        COALESCE(t_umaban.umaban, '') AS umaban,
        COALESCE(t_name.bamei, '') AS bamei,
        COALESCE(t_predict.predict::text, '')::int AS predict,
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
    WHERE t_predict.year = '%s'
    AND t_predict.monthday = '%s'
    AND t_predict.jyocd = '%s'
    AND t_predict.racenum = '%s'
    ORDER BY predict;
    """
    with psycopg2.connect(dbparams) as conn:
        conn.set_client_encoding('UTF8')
        return pd.io.sql.read_sql_query(query % (year, monthday, int(jyocd), int(racenum)), conn)
