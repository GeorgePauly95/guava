CREATE OR REPLACE
FUNCTION haversine_distance(latitude_1 DOUBLE PRECISION, longitude_1 DOUBLE PRECISION, latitude_2 DOUBLE PRECISION, longitude_2 DOUBLE PRECISION)
RETURNS DOUBLE PRECISION AS $$ 
DECLARE
	lat1_rad DOUBLE PRECISION;
	lat2_rad DOUBLE PRECISION;
	delta_lat DOUBLE PRECISION;
	delta_long DOUBLE PRECISION;
	a DOUBLE PRECISION;
	c DOUBLE PRECISION;
	R DOUBLE PRECISION := 6371000.0;
BEGIN
	lat1_rad := radians(latitude_1);
	lat2_rad := radians(latitude_2);
	delta_lat := radians(latitude_2 - latitude_1);
	delta_long := radians(longitude_2 - longitude_1);
 	a := power(sin(delta_lat / 2),2) + cos(lat1_rad) * cos(lat2_rad) * power(sin(delta_long / 2),2);
    c := 2 * atan2(sqrt(a), sqrt(1 - a));

	RETURN R * c;
END;

$$
LANGUAGE PLPGSQL
