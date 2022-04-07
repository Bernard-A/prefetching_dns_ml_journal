import argparse


def get_parser():
    parser = argparse.ArgumentParser("CLI DNS and Prefetch handler ")
    parser.add_argument("input_chain", help="Input Chain Data")
    parser.add_argument("--output_file", "-o", default="cmd.sh", help="Associated command to run")
    return parser


def main():
    args = get_parser().parse_args()
    input_chain = args.input_chain
    cmd_string = pattern(input_chain)

    with open("cmds/" + args.input_chain + "-" + args.output_file, 'w') as output_file:
        output_file.write(cmd_string)
        print("Command to run : " + cmd_string)


def pattern (input_chain):

    match input_chain[0]:
        case "1":
            prefetching_scenario = " -s np "
        case "2":
            prefetching_scenario = " -s pp "
        case "3":
            prefetching_scenario = " -s ml "
        case _:
            raise NotImplementedError("Not handling other cases than NP (1), PP(2) and ML(3)")

    match input_chain[1]:
        case "A":
            duplication_scenario = "hourly"
        case "B":
            duplication_scenario = "daily"
        case _:
            raise NotImplementedError("Not handling other cases than Hourly (A) or Daily (B)")

    match input_chain[2]:
        case "a":
            antenna_locations = "square"
        case "b":
            antenna_locations = "hexa"
        case "c":
            antenna_locations = "random"
        case _:
            raise NotImplementedError("Not handling other cases than Square (a), Hexagonal (b) and Random (c)")

    match input_chain[3]:
        case "X":
            cache_limit = ""
        case "L":
            cache_limit = "-l 2500 "
        case _:
            raise NotImplementedError("Not handling other cases than Unlimited or limited (to 2500)")

    cmd_string = "python main.py " + antenna_locations + "/input_data_" + antenna_locations \
                 + "_" + duplication_scenario + "_split" + prefetching_scenario \
                 + "-a " + antenna_locations + "/Antennas_location_" + antenna_locations + ".csv " \
                 + "-p " + antenna_locations + "/prox_antenna_" + antenna_locations + ".json " + cache_limit \
                 + "-o " + antenna_locations + "/" + input_chain + ".csv"

    return cmd_string



if __name__ == "__main__":
    main()
