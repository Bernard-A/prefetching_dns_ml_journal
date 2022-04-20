import pandas as pd
import json
import os
import argparse
from datetime import datetime

# Initializing global values
# Cache size limit (default 0)
CACHE_MAX_SIZE = 0
CACHE_LIMIT = False
# Initialize antenna cache
dict_antenna = dict()
global prox_antenna
global dataframe_antennas
# Default follow file
follow_file_name = "follow.txt"


def get_parser():
    parser = argparse.ArgumentParser("CLI DNS and Prefetch handler ")
    parser.add_argument("data_input", help="Input Data, file example provided in the documentation")
    parser.add_argument("--scenario", "-s", default="np",
                        help="Chosen scenario, values are np for no-prefetch, pp for proximity prefetch and ml for ml "
                             "prefetch")
    parser.add_argument("--antenna_file", "-a", default="antenna_location.csv",
                        help="Antenna location file, location not used only antenna ids")
    parser.add_argument("--prox_antenna", "-p", default="prox_antenna.csv",
                        help="Antenna disposition file")
    parser.add_argument("--cache_size", "-l", default=0, help="<Integer>, decides upon cache limit (0 for no limit, "
                                                              "default 0)")
    parser.add_argument("--output_file", "-o", default="follow.txt", help="Output file, size of each cache over time")
    parser.add_argument("--antenna_caching_datafile", default="antenna_output.csv",
                        help="Loads mean time for entries in cache")
    parser.add_argument("--logfile", default="log.txt", help="Log the execution input")
    return parser


def main():
    args = get_parser().parse_args()

    with open(args.logfile, 'a') as logfile:
        logfile.write("\n\nStarting algorithm execution\n")
        print("\n\nStarting algorithm execution")
        logfile.write("Arguments are " + str(args)+"\n")
        print("Arguments are " + str(args))
        logfile.write("Algorithm started at " + str(datetime.now()) + "\n")
        print("Algorithm started at " + str(datetime.now()))

    # Loading scenario choice
    scenario = args.scenario

    # Loading mobility data into pandas dataframe
    dataframe_vehicle_movements = pd.read_csv(args.data_input, sep=" ", index_col=False)

    # Loading antennas profile and antenna ids
    global dataframe_antennas
    dataframe_antennas = pd.read_csv(args.antenna_file)
    for identifier in dataframe_antennas.antenna_id:
        dict_antenna[identifier] = {0: 0}
    dataframe_antennas.insert(len(dataframe_antennas.columns), 'expiration_counter', 0)
    dataframe_antennas.insert(len(dataframe_antennas.columns), 'expiration_value_cumulative', 0)
    dataframe_antennas.insert(len(dataframe_antennas.columns), 'expiration_value_mean', 0)

    # Loading antenna_proximity dictionary
    global prox_antenna
    with open(args.prox_antenna) as json_file:
        prox_antenna = json.load(json_file)

    # Loading cache size
    global CACHE_MAX_SIZE
    global CACHE_LIMIT
    CACHE_MAX_SIZE = int(args.cache_size)
    CACHE_LIMIT = (CACHE_MAX_SIZE != 0)

    # Cleaning_up output file
    if os.path.exists(args.output_file):
        print("Please remove previous output file")
        return 0
    else:
        global follow_file_name
        follow_file_name = args.output_file

    prev_time = dataframe_vehicle_movements.sort_values(by=['Time']).iloc[0]['Time']
    dns_requests = 0
    dns_prefetching_requests = 0

    for idx, row in dataframe_vehicle_movements.sort_values(by=['Time']).iterrows():
        current_time = row['Time']
        if current_time != prev_time:
            for i in range(prev_time, current_time):
                antennas_follow_array()
                antenna_dns_expiration(1)
            prev_time = current_time

        dns_requests += dns_request(row['NumTraj'], row['Antenna0'])

        solicited_antennas = antennas_prefetch_handler(row, scenario)
        dns_prefetching_requests += prefetching_request(row['NumTraj'], solicited_antennas)

    with open(args.logfile, 'a') as logfile:
        logfile.write("End of Program\n")
        print("End of Program")
        logfile.write("Number of DNS Requests " + str(dns_requests) + "\n")
        print("Number of DNS Requests " + str(dns_requests))
        logfile.write("Number of Prefetching Requests " + str(dns_prefetching_requests) + "\n")
        print("Number of Prefetching Requests " + str(dns_prefetching_requests))
        logfile.write("Number of Moving devices " + str(len(dataframe_vehicle_movements.index)) + "\n")
        print("Number of Moving devices " + str(len(dataframe_vehicle_movements.index)))
        logfile.write("Output stored as " + str(args.output_file) + "\n")
        print("Output stored as " + str(args.output_file))
        logfile.write("Algorithm ended at " + str(datetime.now()) + "\n")
        print("Algorithm ended at " + str(datetime.now()))

    dataframe_antennas.expiration_value_mean = \
        dataframe_antennas.expiration_value_cumulative / dataframe_antennas.expiration_counter
    dataframe_antennas.to_csv(args.antenna_caching_datafile)


def antenna_dns_expiration(delay):
    # This function removes <delay> time from the antennas cache and pops expired data from the dictionaries
    # In : delay (int)

    for antenna_identifier in dict_antenna:
        outlist = []
        for numTraj in dict_antenna[antenna_identifier]:
            dict_antenna[antenna_identifier][numTraj] = dict_antenna[antenna_identifier][numTraj] - delay
            if dict_antenna[antenna_identifier][numTraj] <= 0:
                outlist.append(numTraj)
        for numTraj in outlist:
            dict_antenna[antenna_identifier].pop(numTraj)
            dataframe_antennas.loc[dataframe_antennas.antenna_id == antenna_identifier, 'expiration_counter'] += 1
            dataframe_antennas.loc[
                dataframe_antennas.antenna_id == antenna_identifier, 'expiration_value_cumulative'] += 300


def antennas_follow_array():
    # This function logs the size of each antenna's cache

    # Data string
    written_string = ""
    for antenna_identifier in dict_antenna:
        written_string += (str(len(dict_antenna[antenna_identifier])) + ",")
    written_string += "\n"

    # Write the string to associated log file
    with open(follow_file_name, 'a') as follow_file:
        follow_file.write(written_string)


def dns_request(vehicle_id, antenna_id):
    # This function adds DNS entry to antenna cache and logs possible antenna cache overload
    # In : vehicle_id (int), antenna_id (int)
    if dict_antenna[antenna_id].get(vehicle_id, 0) <= 0:
        dict_antenna[antenna_id][vehicle_id] = 300
        if CACHE_LIMIT and (len(dict_antenna[antenna_id]) > CACHE_MAX_SIZE):
            cache_limit_handler(antenna_id)
        return 1
    return 0


def prefetching_request(vehicle_id, antenna_ids):
    # This function realises the prefetching operations
    # In : vehicle_id (int), antenna_ids (int array)

    # Escape the function if antenna_ids array is empty
    if not antenna_ids:
        return 0

    # count the number of dns prefetching requests performed
    dns_prefetching_count = 0

    for antenna_id in antenna_ids:
        dns_prefetching_count += dns_request(vehicle_id, antenna_id)

    return dns_prefetching_count


def antennas_prefetch_handler(row_handled, scenario):
    solicited_antenna_array = []
    match scenario:
        case "np":
            return solicited_antenna_array
        case "pp":
            if row_handled['Antenna1'] != 0:
                for antenna in prox_antenna[str(row_handled['Antenna0'])]:
                    solicited_antenna_array.append(antenna)
            return solicited_antenna_array
        case "ml":
            solicited_antenna_array.append(row_handled['Antenna1'])
            solicited_antenna_array.append(row_handled['Antenna2'])
            solicited_antenna_array.append(row_handled['Antenna3'])
            solicited_antenna_array.append(row_handled['Antenna4'])
            solicited_antenna_array = list(filter(lambda an_id: an_id != 0, solicited_antenna_array))
            return solicited_antenna_array
        case _:
            raise NotImplementedError("Not handling other cases than NP, PP and ML")


def cache_limit_handler(antenna_id):

    min_val = dict_antenna[antenna_id][min(dict_antenna[antenna_id], key=dict_antenna[antenna_id].get)]
    del dict_antenna[antenna_id][min(dict_antenna[antenna_id], key=dict_antenna[antenna_id].get)]

    dataframe_antennas.loc[dataframe_antennas.antenna_id == antenna_id, 'expiration_counter'] += 1
    dataframe_antennas.loc[
        dataframe_antennas.antenna_id == antenna_id, 'expiration_value_cumulative'] += (300-min_val)


if __name__ == "__main__":
    main()
