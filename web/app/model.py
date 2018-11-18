# coding:utf-8
import os
import psycopg2
import pandas as pd

dbparams = "host={} user={} port={} password={}".format(
        os.environ['DATABASE_HOST'],
        os.environ['DATABASE_USER'],
        os.environ['DATABASE_PORT'],
        os.environ['DATABASE_PASSWORD']
    )

def prediction():
    query = """
    SELECT
        COALESCE(t_umaban.umaban, '') AS umaban,
        COALESCE(t_name.bamei, '') AS bamei,
        COALESCE(t_predict.predict::text, '') AS predict,
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
        AND t_predict.kettonum = t_umaban.kettonum;
    """
    with psycopg2.connect(dbparams) as conn:
        return pd.io.sql.read_sql_query(query, conn)