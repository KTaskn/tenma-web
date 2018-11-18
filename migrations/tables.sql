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