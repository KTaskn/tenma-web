CREATE TABLE t_name
(
	kettonum character varying(10) NOT NULL,
	bamei character varying(36) NOT NULL,
	PRIMARY KEY (kettonum)
);

CREATE TABLE t_umaban
(
	year character varying(4) NOT NULL,
	monthday character varying(4) NOT NULL,
	jyocd character varying(2) NOT NULL,
	racenum character varying(2) NOT NULL,
	kettonum character varying(10) NOT NULL,
	umaban character varying(2) NOT NULL,
	PRIMARY KEY (year, monthday, jyocd, racenum, kettonum)
);

CREATE TABLE t_actual
(
	year character varying(4) NOT NULL,
	monthday character varying(4) NOT NULL,
	jyocd character varying(2) NOT NULL,
	racenum character varying(2) NOT NULL,
	kettonum character varying(10) NOT NULL,
	actual INTEGER NOT NULL,
	PRIMARY KEY (year, monthday, jyocd, racenum, kettonum)
);

CREATE TABLE t_predict
(
	year character varying(4) NOT NULL,
	monthday character varying(4) NOT NULL,
	jyocd character varying(2) NOT NULL,
	racenum character varying(2) NOT NULL,
	kettonum character varying(10) NOT NULL,
	predict INTEGER NOT NULL,
	PRIMARY KEY (year, monthday, jyocd, racenum, kettonum)
);

CREATE TABLE t_umatan(
	year character varying(4) NOT NULL,
	monthday character varying(4) NOT NULL,
	jyocd character varying(2) NOT NULL,
	racenum character varying(2) NOT NULL,
	kettonum_1chaku character varying(10) NOT NULL,
	kettonum_2chaku character varying(10) NOT NULL,
	odds REAL NOT NULL,
	PRIMARY KEY (year, monthday, jyocd, racenum, kettonum_1chaku, kettonum_2chaku)
);

CREATE TABLE t_factor
(
	year character varying(4) NOT NULL,
	monthday character varying(4) NOT NULL,
	jyocd character varying(2) NOT NULL,
	racenum character varying(2) NOT NULL,
	kettonum character varying(10) NOT NULL,
	factor character varying(32) NOT NULL,
	score REAL NOT NULL,
	PRIMARY KEY (year, monthday, jyocd, racenum, kettonum, factor)
);

CREATE TABLE t_racename
(
	year character varying(4) NOT NULL,
	monthday character varying(4) NOT NULL,
	jyocd character varying(2) NOT NULL,
	racenum character varying(2) NOT NULL,
	racename character varying(64),
	PRIMARY KEY (year, monthday, jyocd, racenum)
);