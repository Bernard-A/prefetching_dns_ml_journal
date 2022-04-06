# prefetching_dns_ml_journal

# The scripts work as follow
Run the time_vehicle_deduplication.sh script to generate the data for the python scripts

Then run the python script with the necessary parameters

e.g. 

```bash
python main.py Hexa/input_data_hexa_hourly_split -s pp -a Hexa/Antennas_location_hexa.csv -p Hexa/prox_antenna_hexa.json -l 200 -o Hexa/2AbL.csv
```
To run the script on the hexa input data considering proximity-based prefetching and setting a DNS cache limit to 200 entries

A Makefile will follow to generate all datasets
A run.sh script will follo to run all scenarios
