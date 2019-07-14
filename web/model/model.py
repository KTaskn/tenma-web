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
    TO_CHAR(t_race.racedate, 'yyyymmdd') AS racedate_id,
    TO_CHAR(t_race.racedate, 'yyyy年mm月dd日') AS racedate_disp,
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
    for racedate_id, racedate_disp, keibajyo_name, racenum in df.values:
        l_text.append("%s %sR %s" % (racedate_disp, racenum, keibajyo_name))
        l_key.append("%s%s%s" % (racedate_id, keibajyo_name, racenum))
    return l_text, l_key

def races_day(date):
    query = """
    SELECT
    TO_CHAR(t_race.racedate, 'yyyymmdd') AS racedate_id,
    TO_CHAR(t_race.racedate, 'yyyy年mm月dd日') AS racedate_disp,
    LPAD(t_race.keibajyo_id::text, 2, '0') AS keibajyo_id,
    t_keibajyo.name AS keibajyo_name,
    LPAD(t_race.racenum::text, 2, '0') AS racenum
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
    for racedate_id, racedate_disp, keibajyo_id, keibajyo_name, racenum in df.values:
        l_text.append("%s %s %sR" % (racedate_disp, keibajyo_name, racenum))
        l_key.append("%s%s%s" % (racedate_id, keibajyo_id, racenum))
    return l_text, l_key

def racedays():
    query = """
    SELECT
    DISTINCT 
    TO_CHAR(t_race.racedate, 'yyyymmdd') AS racedate_id,
    TO_CHAR(t_race.racedate, 'yyyy年mm月dd日') AS racedate_disp
    FROM t_race
    ORDER BY racedate_id DESC LIMIT 12;
    """

    with psycopg2.connect(dbparams) as conn:
        conn.set_client_encoding('UTF8')
        df = pd.io.sql.read_sql_query(query, conn)
        
    return list(zip(
        df['racedate_id'].values.tolist(),
        df['racedate_disp'].values.tolist()
    ))

def keibajyo(date):
    query = """
    SELECT
    DISTINCT
    LPAD(t_race.keibajyo_id::text, 2, '0') AS keibajyo_id,
    t_keibajyo.name AS keibajyo_name
    FROM t_race
    INNER JOIN t_keibajyo ON t_race.keibajyo_id = t_keibajyo.id
    WHERE t_race.racedate = DATE('%s')
    ORDER BY keibajyo_id ASC;
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
    DISTINCT LPAD(t_race.racenum::text, 2, '0') AS racenum
    FROM t_race
    WHERE t_race.racedate = DATE('%s') AND t_race.keibajyo_id = %s
    ORDER BY racenum ASC;
    """

    with psycopg2.connect(dbparams) as conn:
        conn.set_client_encoding('UTF8')
        df = pd.io.sql.read_sql_query(query % (date, keibajyo_id), conn)
    
    return df['racenum'].values.tolist()

def prediction(date, keibajyo_id, racenum):
    import numpy as np
    BIAS = 0.001
    query = """
    select
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
    and t_horserace.keibajyo_id = {keibajyo_id}
    and t_horserace.racenum = {racenum};
    """
    with psycopg2.connect(dbparams) as conn:
        conn.set_client_encoding('UTF8')
        df = pd.io.sql.read_sql_query(query.format(date=date, keibajyo_id=keibajyo_id, racenum=racenum, bias=BIAS), conn)

    f_log = np.log
    df['pa'] = f_log(1 / 18.0)
    for col in ['horse', 'sire', 'broodmare', 'kisyu']:
        pa_col = "pa_%s" % col
        pab_col = "pab_%s" % col
        df['pa'] = df[pab_col].map(f_log) - df[pa_col].map(f_log) + df['pa']

    df['pa'] = df['pa'].map(np.exp) / df['pa'].map(np.exp).sum()
    df['score'] = (1.0 / df['pa']).round(1)
    df['predict'] = df['score'].rank()
    return df[['horse_id', 'name', 'predict', 'score']].sort_values('predict')

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

def get_hist_horse(horse_id):
    query = """
    select
    t_horserace.kakuteijyuni,
    sum(1) as _count
    from t_horserace
    inner join t_race on t_horserace.racedate = t_race.racedate
    and t_horserace.keibajyo_id = t_race.keibajyo_id
    and t_horserace.racenum = t_race.racenum
    where t_horserace.horse_id = %s
    group by t_horserace.kakuteijyuni
    """

    with psycopg2.connect(dbparams) as conn:
        conn.set_client_encoding('UTF8')
        df = pd.io.sql.read_sql_query(query % (horse_id), conn)

    return pd.merge(
        pd.DataFrame({'kakuteijyuni': list(range(1, 19))}),
        df
    ).sort_values('kakuteijyuni')['_count'].tolist()

def get_hist_sire(sire_id, kyori, course_id):
    query = """
    select
    t_horserace.kakuteijyuni,
    sum(1) as _count
    from t_horserace
    inner join t_horse on t_horserace.horse_id = t_horse.id
    inner join t_race on t_horserace.racedate = t_race.racedate
    and t_horserace.keibajyo_id = t_race.keibajyo_id
    and t_horserace.racenum = t_race.racenum
    where t_horse.sire_id = %s and t_race.kyori = %s and t_race.course_id = %s
    group by t_horserace.kakuteijyuni
    """

    with psycopg2.connect(dbparams) as conn:
        conn.set_client_encoding('UTF8')
        df = pd.io.sql.read_sql_query(query % (sire_id, kyori, course_id), conn)

    return pd.merge(
        pd.DataFrame({'kakuteijyuni': list(range(1, 19))}),
        df
    ).sort_values('kakuteijyuni')['_count'].tolist()

def get_hist_broodmare(broodmare_id):
    query = """
    select
    t_horserace.kakuteijyuni,
    sum(1) as _count
    from t_horserace
    inner join t_horse on t_horserace.horse_id = t_horse.id
    inner join t_race on t_horserace.racedate = t_race.racedate
    and t_horserace.keibajyo_id = t_race.keibajyo_id
    and t_horserace.racenum = t_race.racenum
    where t_horse.broodmare_id = %s
    group by t_horserace.kakuteijyuni
    """

    with psycopg2.connect(dbparams) as conn:
        conn.set_client_encoding('UTF8')
        df = pd.io.sql.read_sql_query(query % (broodmare_id), conn)

    return pd.merge(
        pd.DataFrame({'kakuteijyuni': list(range(1, 19))}),
        df
    ).sort_values('kakuteijyuni')['_count'].tolist()

def get_hist_kisyu(kisyu_id, date):
    query = """
    select
    t_horserace.kakuteijyuni,
    sum(1) as _count
    from t_horserace
    where t_horserace.kisyu_id = %s and t_horserace.racedate > DATE('%s') - 30
    group by t_horserace.kakuteijyuni
    """

    with psycopg2.connect(dbparams) as conn:
        conn.set_client_encoding('UTF8')
        df = pd.io.sql.read_sql_query(query % (kisyu_id, date), conn)

    return pd.merge(
        pd.DataFrame({'kakuteijyuni': list(range(1, 19))}),
        df
    ).sort_values('kakuteijyuni')['_count'].tolist()

def get_hist(date, keibajyo_id, racenum, horse_id):
    query = """
    select horse_id, kisyu_id, course_id, kyori, sire_id, broodmare_id from t_horserace
    inner join t_horse on t_horserace.horse_id = t_horse.id
    inner join t_race on t_horserace.racedate = t_race.racedate
    and t_horserace.keibajyo_id = t_race.keibajyo_id
    and t_horserace.racenum = t_race.racenum
    where t_horserace.racedate = DATE('%s')
    and t_horserace.keibajyo_id = %s
    and t_horserace.racenum = %s
    and t_horserace.horse_id = %s
    """

    with psycopg2.connect(dbparams) as conn:
        conn.set_client_encoding('UTF8')
        df = pd.io.sql.read_sql_query(query % (date, keibajyo_id, racenum, horse_id), conn)
    
    if len(df.index) > 1:
        app.logger.warning('データが複数ある')
        raise Exception('データが複数ある')

    elif len(df.index) == 1:
        row = df.iloc[0]
        return {
            "hist_horse": get_hist_horse(horse_id),
            "hist_sire": get_hist_sire(row['sire_id'], row['kyori'], row['course_id']),
            "hist_broodmare": get_hist_broodmare(row['broodmare_id']),
            "hist_kisyu": get_hist_kisyu(row['kisyu_id'], date)
        }
    else:
        app.logger.warning('データがない')
        raise Exception('データがない')