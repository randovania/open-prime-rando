import argparse


def create_parser():
    parser = argparse.ArgumentParser()
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    print(args)
