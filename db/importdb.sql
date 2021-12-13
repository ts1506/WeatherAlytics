CREATE DATABASE weatheralytics;
USE weatheralytics;
CREATE TABLE weatherHistory (id INT NOT NULL AUTO_INCREMENT, reading_time TIMESTAMP NOT NULL, summary VARCHAR(255) NOT NULL, precip_type VARCHAR(255) NOT NULL, temperature DOUBLE NOT NULL, apparent_temperature DOUBLE NOT NULL, humidity double NOT NULL, wind_speed DOUBLE NOT NULL, wind_bearing INT NOT NULL, visibility DOUBLE NOT NULL, loud_cover INT NOT NULL, pressure DOUBLE NOT NULL, daily_summary VARCHAR(255) NOT NULL, PRIMARY KEY (id));
SET GLOBAL local_infile=1;
LOAD DATA LOCAL INFILE '~/Documents/VSCode/Weatheralytics/dataset/weatherHistory.csv' INTO TABLE weatherHistory FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' IGNORE 1 ROWS (reading_time, summary, precip_type, temperature, apparent_temperature, humidity, wind_speed, wind_bearing, visibility, loud_cover, pressure, daily_summary, id);
ALTER TABLE weatherHistory DROP COLUMN loud_cover;
ALTER TABLE weatherHistory DROP COLUMN daily_summary;
