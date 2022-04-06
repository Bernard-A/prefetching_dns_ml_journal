make: hexa square random

clean:
	rm -rf hexa/input_data_hexa_daily_split hexa/input_data_hexa_hourly_split square/input_data_square_daily_split square/input_data_square_hourly_split random/input_data_random_daily_split random/input_data_random_hourly_split

hexa:
	sh time_vehicle_deduplication.sh hexa/input_data_hexa

square:
	sh time_vehicle_deduplication.sh square/input_data_square
	
random:
	sh time_vehicle_deduplication.sh random/input_data_random

