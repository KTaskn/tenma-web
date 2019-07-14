CREATE TABLE t_keibajyo
(
	id serial NOT NULL,
	name character varying(36) NOT NULL,
	PRIMARY KEY (id)
);
INSERT INTO t_keibajyo (id, name) VALUES
(0, 'その他'),
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


CREATE TABLE t_course
(
	id serial NOT NULL,
	name character varying(36) NOT NULL,
	PRIMARY KEY (id)
);
INSERT INTO t_course (id, name) VALUES
(0, 'その他'),
(1, '芝'),
(2, 'ダート'),
(3, '障害');

CREATE TABLE t_class
(
	id serial NOT NULL,
	name character varying(36) NOT NULL,
	PRIMARY KEY (id)
);
INSERT INTO t_class (id, name) VALUES
(0, 'その他'),
(1, '新馬'),
(2, '未勝利'),
(3, '１勝'),
(4, '２勝'),
(5, '３勝'),
(6, 'オープン'),
(7, 'Ｇ３'),
(8, 'Ｇ２'),
(9, 'Ｇ１');


CREATE TABLE t_race
(
	keibajyo_id serial references t_keibajyo(id),
	racedate date NOT NULL,
	racenum int NOT NULL,
	course_id serial references t_course(id),
	class_id serial references t_class(id),
	kyori int NOT NULL,
	name character varying(36),
	PRIMARY KEY (keibajyo_id, racedate, racenum)
);

CREATE TABLE t_sire
(
	id serial NOT NULL,
	name character varying(36) NOT NULL,
	PRIMARY KEY (id)
);
insert into t_sire (id, name) VALUES (0, '未登録');

CREATE TABLE t_broodmare
(
	id serial NOT NULL,
	name character varying(36) NOT NULL,
	PRIMARY KEY (id)
);
insert into t_broodmare (id, name) VALUES (0, '未登録');

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
insert into t_kisyu (id, name) VALUES (0, '未登録');

CREATE TABLE t_horserace
(
	keibajyo_id serial references t_keibajyo(id),
	racedate date NOT NULL,
	racenum int NOT NULL,
	horse_id serial references t_horse(id),
	kisyu_id serial references t_kisyu(id),
	kakuteijyuni int DEFAULT NULL,
	PRIMARY KEY (keibajyo_id, racedate, racenum, horse_id)
);