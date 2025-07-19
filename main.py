"""
API Load Pro - Universal Python REST API Data Creator
A command-line utility for automating test data creation via REST APIs.
"""

import argparse
import configparser
import sys
from Libraries.config_manager import ConfigManager

def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.
    Returns:
    Parsed command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="API-Load Pro - Universal Python REST API Data Creator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
        Examples:
        python main.py --data-file sample_data.json
        python main.py -d test_data.json --verbose
        """
    )

    parser.add_argument(
        '-d', '--data-file',
        required=True,
        help='The path to the JSON file containing the test data & API requests'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output for detailed requests information'
    )

    parser.add_argument(
        '--config',
        default='config.ini',
        help='The path to the configuration file(defaults to config.ini)'
    )

    parser.add_argument(
        '--no-save',
        action='store_true',
        help='Do not save the test data & API requests'
    )

    parser.add_argument(
        '--result-dir',
        default='results',
        help='The directory to save the test data & API requests(defaults to results)'
    )

    return parser.parse_args()

def main():
    """ Main entry point for the API Load Pro Utility """
    print("_"*50)
    print("API Load Pro - Universal Python REST API Data Creator")
    print("_"*50)

    args = parse_arguments()

    try:
        config_manager = configparser.ConfigParser(args.config)
        config = ConfigManager.load_config()

        print(f"Configuration loaded from {args.config}")


    except FileNotFoundError as e:
        print(f" Error: {e}")
        sys.exit(1)

    except Exception as e:
        print(f" Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
