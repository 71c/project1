-- Adminer 4.6.3-dev PostgreSQL dump

\connect "danltck14i7gdv";

DROP TABLE IF EXISTS "accounts";
DROP SEQUENCE IF EXISTS accounts_id_seq;
CREATE SEQUENCE accounts_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1;

CREATE TABLE "public"."accounts" (
    "id" integer DEFAULT nextval('accounts_id_seq') NOT NULL,
    "username" character varying NOT NULL,
    "password" character varying NOT NULL,
    CONSTRAINT "accounts_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "accounts_username_key" UNIQUE ("username")
) WITH (oids = false);


DROP TABLE IF EXISTS "checkins";
CREATE TABLE "public"."checkins" (
    "user_id" integer,
    "zipcode" character varying,
    "comment" character varying,
    CONSTRAINT "checkins_user_id_fkey" FOREIGN KEY (user_id) REFERENCES accounts(id) NOT DEFERRABLE,
    CONSTRAINT "checkins_zipcode_fkey" FOREIGN KEY (zipcode) REFERENCES locations(zipcode) NOT DEFERRABLE
) WITH (oids = false);


DROP TABLE IF EXISTS "locations";
CREATE TABLE "public"."locations" (
    "zipcode" character varying NOT NULL,
    "city" character varying NOT NULL,
    "state" character varying NOT NULL,
    "latitude" numeric NOT NULL,
    "longitude" numeric NOT NULL,
    "population" integer NOT NULL,
    CONSTRAINT "locations_pkey" PRIMARY KEY ("zipcode"),
    CONSTRAINT "locations_zipcode_key" UNIQUE ("zipcode")
) WITH (oids = false);


-- 2018-07-12 22:02:03.714053+00
