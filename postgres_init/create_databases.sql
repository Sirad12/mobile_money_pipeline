CREATE DATABASE mobile_money_db;

--- Commande psql qui signifie "connecte-toi maintenant à cette base"
\c mobile_money_db 

CREATE SCHEMA IF NOT EXISTS raw; ---Les donnees brutes
CREATE SCHEMA IF NOT EXISTS staging; 
CREATE SCHEMA IF NOT EXISTS marts; ---Les donnees nettoyees et pretes a etre analysees


CREATE DATABASE metabase_db;