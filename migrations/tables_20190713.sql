DROP TABLE t_name;
DROP TABLE t_umaban;
DROP TABLE t_actual;
DROP TABLE t_predict;
DROP TABLE t_umatan;
DROP TABLE t_factor;
DROP TABLE t_racename;
DROP TABLE t_odds;

CREATE TABLE t_keibajyo
(
	id serial NOT NULL,
	name character varying(36) NOT NULL,
	PRIMARY KEY (id)
);
INSERT INTO t_keibajyo (id, name) VALUES
(1, '札幌'),
(2, '函館'),
(3, '福島'),
(4, '新潟'),
(5, '東京'),
(6, '中山'),
(7, '中京'),
(8, '京都'),
(9, '阪神'),
(10, '小倉');

CREATE TABLE t_race
(
	id serial NOT NULL,
	keibajyo_id serial references t_keibajyo(id),
	racedate date NOT NULL,
	racenum int NOT NULL,
	name character varying(36),
	PRIMARY KEY (id),
	UNIQUE (keibajyo_id, racedate, racenum)
);

CREATE TABLE t_course
(
	id serial NOT NULL,
	name character varying(36) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE t_class
(
	id serial NOT NULL,
	name character varying(36) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE t_jyoken
(
	race_id serial references t_race(id),
	kyori int NOT NULL,
	course serial references t_course(id),
	class serial references t_class(id),
	UNIQUE (race_id)
);

CREATE TABLE t_sire
(
	id serial NOT NULL,
	name character varying(36) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE t_broodmare
(
	id serial NOT NULL,
	name character varying(36) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE t_horse
(
	id serial NOT NULL,
	name character varying(36) NOT NULL,
	sire_id serial references t_sire(id),
	broodmare_id serial references t_broodmare(id),
	PRIMARY KEY (id)
);

CREATE TABLE t_kisyu
(
	id serial NOT NULL,
	name character varying(36) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE t_horserace
(
	race_id serial references t_race(id),
	horse_id serial references t_horse(id),
	kisyu_id serial references t_kisyu(id),
	kakuteijyuni int DEFAULT NULL,
	UNIQUE (race_id, kisyu_id)
);