"""
Command-line interface (CLI) for the ride-hailing data generator.

This module is the entry point for generating ride-hailing records.
It parses command-line arguments, builds a RuntimeConfig object,
and outputs generated ride records in JSON format.

The core generation logic is implemented in the 'generator/' package.

Usage:
    python data_generator.py                    # Generate 1 record
    python data_generator.py --count 10         # Generate 10 records
    python data_generator.py --debug            # Generate 1 record with debug logs
    python data_generator.py --count 5 --debug  # Generate 5 records with debug logs
"""

import argparse

from generator.modes import generate, historical, eventhub


def _build_parser():
    parser = argparse.ArgumentParser(
        description="...",
    )
    subparsers = parser.add_subparsers(
        dest = "command",
        metavar = "MODE"
    )

    # --- generate ---
    parser_generate = subparsers.add_parser(
        "generate", 
        help = 'Generates ride records based on CLI arguments and prints them as JSON.'
    )
    parser_generate.add_argument(
        "--count", type = int, default = 1, metavar = "N",
        help = "Number of records to generate (default: 1)."
    )
    parser_generate.add_argument(
        "--debug",
        action = "store_true",
        default = False,
        help = "Enable debug logs for geocoding."
    )

    # --- historical ---
    parser_historical = subparsers.add_parser(
        "historical", 
        help = 'Create ride record'
    )
    parser_historical.add_argument(
        "--count", type = int, default = 1, metavar = "N",
        help = "Number of records to generate (default: 1)."
    )
    parser_historical.add_argument(
        "--format", choices = ["json", "csv"],
        required = True,
        help = "Output format: json , csv"
    )
    parser_historical.add_argument(
        "--duration",
        metavar = "START:END",
        required = True,
        help = "Date range for generated timestamps. Format: YYYY-MM-DD:YYYY-MM-DD (e.g. 2024-01-01:2025-01-01)."
    )

    # --- eventhub ---
    parser_eventhub = subparsers.add_parser(
        "eventhub",
        help="Send ride records to Azure Event Hub."
    )
    parser_eventhub.add_argument(
        "--mode", choices=["single", "stream"],
        required=True,
        help="single: send one record. stream: send continuously."
    )
    parser_eventhub.add_argument(
        "--interval", type=float, default=1.0,
        help="Seconds between sends in stream mode (default: 1.0)."
    )
    parser_eventhub.add_argument(
        "--count", type=int, default=0, metavar="N",
        help="Number of records to stream. 0 means run until Ctrl+C (default: 0)."
    )
    parser_eventhub.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Enable debug logs for geocoding."
    )

    return parser


def main():
    """Generates ride records based on CLI arguments and prints them as JSON."""
    parser = _build_parser()
    args = parser.parse_args()

    _command_map = {
        "generate"  : generate.run,
        "historical": historical.run,
        "eventhub"  : eventhub.run,
    }
    _command_map[args.command](args)

    #debug
    # print(args)

if __name__ == "__main__":
    main()
