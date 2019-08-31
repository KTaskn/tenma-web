
# coding:utf-8
import sys
import argparse
import psycopg2
import pandas as pd

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--host', type=str)
    parser.add_argument('--user', type=str)
    parser.add_argument('--dbname', type=str)
    parser.add_argument('--port', type=str)
    parser.add_argument('--password', type=str)
    parser.add_argument('--year', type=str)
    parser.add_argument('--monthday', type=str)
    parser.add_argument('--updateonly', type=bool, default=False)
    args = parser.parse_args()

    dbparams = "host={host} user={user} dbname={dbname} port={port} password={password}".format(
            host=args.host,
            user=args.user,
            dbname=args.dbname,
            port=args.port,
            password=args.password
        )
    
    query = '''select
case
when n_race.jyocd in ('01', '02', '03', '04', '05', '06', '07', '08', '09', '10') then n_race.jyocd::int
else 0
end
as keibajyo_id,
date(concat(n_race.year, n_race.monthday)) as racedate,
n_race.racenum::int as racenum,
case
when trackcd::int >= 10 and trackcd::int <= 22 then 1
when trackcd::int >= 23 and trackcd::int <= 29 then 2
when trackcd::int >= 51 and trackcd::int <= 59 then 3
else 0
end as course_id,
case n_race.jyokencd5
WHEN '701' THEN 1
WHEN '703' THEN 2
WHEN '005' THEN 3
WHEN '010' THEN 4
WHEN '016' THEN 5
WHEN '999' THEN
	CASE n_race.gradecd
		WHEN 'A' THEN 9
		WHEN 'F' THEN 9
		WHEN 'B' THEN 8
		WHEN 'G' THEN 8
		WHEN 'C' THEN 7
		WHEN 'H' THEN 7
		ELSE 6
	END
ELSE 0
END AS class_id,
n_race.kyori AS kyori,
n_race.hondai AS race_name,
n_uma_race.kisyucode::int as kisyu_id,
CASE WHEN n_kisyu.kisyuname IS NULL THEN '' ELSE n_kisyu.kisyuname END as kisyu_name,
n_uma_race.kettonum::int as uma_id,
n_uma_race.bamei as uma_name,
CASE WHEN n_uma.Ketto3InfoHansyokuNum1 IS NULL THEN 0 ELSE n_uma.Ketto3InfoHansyokuNum1::int END as sire_id,
CASE WHEN n_uma.ketto3infobamei1 IS NULL THEN '' ELSE n_uma.ketto3infobamei1 END as sire_name,
CASE WHEN n_uma.Ketto3InfoHansyokuNum2 IS NULL THEN 0 ELSE n_uma.Ketto3InfoHansyokuNum2::int END as broodmare_id,
CASE WHEN n_uma.ketto3infobamei2 IS NULL THEN '' ELSE n_uma.ketto3infobamei2 END as broodmare_name,
n_uma_race.kakuteijyuni::int as kakuteijyuni
from n_race
left join n_uma_race
on n_race.year = n_uma_race.year
and n_race.monthday = n_uma_race.monthday
and n_race.jyocd = n_uma_race.jyocd
and n_race.racenum = n_uma_race.racenum
left join n_uma on n_uma_race.kettonum = n_uma.kettonum
left join n_kisyu on n_uma_race.kisyucode = n_kisyu.kisyucode
WHERE n_race.year::int >= 2016
and n_race.jyocd in ('01', '02', '03', '04', '05', '06', '07', '08', '09', '10')
and n_race.year = '{year}'
and n_race.monthday = '{monthday}'
'''

    with psycopg2.connect(dbparams) as conn:
        df = pd.io.sql.read_sql_query(
            query.format(year=args.year, monthday=args.monthday),
            conn
        )

    if args.updateonly == False:
        for idx, grp in df.groupby(['keibajyo_id', 'racedate', 'racenum', 'course_id', 'class_id', 'kyori', 'race_name']):
            query = '''INSERT INTO "t_race" ("keibajyo_id","racedate","racenum","course_id","class_id","kyori","name") 
SELECT {keibajyo_id}, E'{racedate}', {racenum}, {course_id}, {class_id}, E'{kyori}', E'{name}'
WHERE NOT EXISTS (
    SELECT keibajyo_id, racedate, racenum FROM t_race
    WHERE keibajyo_id = {keibajyo_id}
    AND racedate = E'{racedate}'
    AND racenum = {racenum}
);'''
            print(query.format(
                keibajyo_id=idx[0],
                racedate=idx[1],
                racenum=idx[2],
                course_id=idx[3],
                class_id=idx[4],
                kyori=idx[5],
                name=idx[6].replace("'", "s")
            ).replace("\n", ""))

        for idx, grp in df.groupby(['sire_id', 'sire_name']):
            query = '''INSERT INTO "t_sire" ("id", "name") 
SELECT {sire_id}, E'{sire_name}'
WHERE NOT EXISTS (
    SELECT id FROM t_sire
    WHERE id = {sire_id}
);'''
            print(query.format(
                sire_id=idx[0],
                sire_name=idx[1].replace("'", "s"),
            ).replace("\n", ""))

        for idx, grp in df.groupby(['broodmare_id', 'broodmare_name']):
            query = '''INSERT INTO "t_broodmare" ("id", "name") 
SELECT {broodmare_id}, E'{broodmare_name}'
WHERE NOT EXISTS (
    SELECT id FROM t_broodmare
    WHERE id = {broodmare_id}
);'''
            print(query.format(
                broodmare_id=idx[0],
                broodmare_name=idx[1].replace("'", "s"),
            ).replace("\n", ""))

        for idx, grp in df.groupby(['uma_id', 'uma_name', 'sire_id', 'broodmare_id']):
            query = '''INSERT INTO "t_horse" ("id", "name", "sire_id", "broodmare_id") 
SELECT {uma_id}, E'{uma_name}', {sire_id}, {broodmare_id}
WHERE NOT EXISTS (
    SELECT id FROM t_horse
    WHERE id = {uma_id}
);'''
            print(query.format(
                uma_id=idx[0],
                uma_name=idx[1].replace("'", "s"),
                sire_id=idx[2],
                broodmare_id=idx[3],
            ).replace("\n", ""))

        for idx, grp in df.groupby(['kisyu_id', 'kisyu_name']):
            query = '''INSERT INTO "t_kisyu" ("id", "name") 
SELECT {kisyu_id}, E'{kisyu_name}'
WHERE NOT EXISTS (
    SELECT id FROM t_kisyu
    WHERE id = {kisyu_id}
);'''
            print(query.format(
                kisyu_id=idx[0],
                kisyu_name=idx[1].replace("'", "s"),
            ).replace("\n", ""))

    for idx, grp in df.groupby(['keibajyo_id', 'racedate', 'racenum', 'uma_id', 'kisyu_id', 'kakuteijyuni']):

        if args.updateonly == False:
            query = '''INSERT INTO "t_horserace" ("keibajyo_id", "racedate", "racenum", "horse_id", "kisyu_id", "kakuteijyuni") 
SELECT {keibajyo_id}, E'{racedate}', {racenum}, {horse_id}, {kisyu_id}, {kakuteijyuni}
WHERE NOT EXISTS (
    SELECT keibajyo_id, racedate, racenum, horse_id FROM t_horserace
    WHERE keibajyo_id = {keibajyo_id}
    AND racedate = E'{racedate}'
    AND racenum = {racenum}
    AND horse_id = {horse_id}
);'''
            print(query.format(
                keibajyo_id=idx[0],
                racedate=idx[1],
                racenum=idx[2],
                horse_id=idx[3],
                kisyu_id=idx[4],
                kakuteijyuni=idx[5]
            ).replace("\n", ""))

        query = '''UPDATE "t_horserace" SET kakuteijyuni = {kakuteijyuni} WHERE keibajyo_id = {keibajyo_id}
    AND racedate = E'{racedate}'
    AND racenum = {racenum}
    AND horse_id = {horse_id}
;'''
        print(query.format(
            keibajyo_id=idx[0],
            racedate=idx[1],
            racenum=idx[2],
            horse_id=idx[3],
            kakuteijyuni=idx[5]
        ).replace("\n", ""))