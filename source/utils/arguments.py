import argparse


def process_args():
    # Initialize argument parser
    parser = argparse.ArgumentParser()

    # Adding arguments
    parser.add_argument('--test', action='store_true', help='Enable test mode')

    # Parsing arguments
    args = parser.parse_args()

    return args