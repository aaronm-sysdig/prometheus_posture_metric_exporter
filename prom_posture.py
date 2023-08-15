"""
This script collects and exposes Sysdig metrics for Prometheus.

It provides functionalities like:
- Parsing and validating configuration from a YAML file.
- Fetching data from the Sysdig API.
- Processing and exposing metrics in a format suitable for Prometheus.

Usage:
    python script_name.py -c /path/to/config.yaml
"""

import logging
import time
import requests
import yaml
import argparse
from urllib.parse import urljoin
from prometheus_client import start_http_server, REGISTRY
from prometheus_client.core import GaugeMetricFamily

auth_header = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Authorization": ""  # Will be set to "Bearer {token}" later in the code
}


def parse_arguments():
    """
    Parses command-line arguments.

    :return: A namespace containing the arguments provided by the user.
    """
    parser = argparse.ArgumentParser(description="A script to collect and expose Sysdig metrics for Prometheus.")

    # Argument for the configuration file
    parser.add_argument("-c", "--config", type=str, required=True,
                        help="Path to the configuration YAML file.")

    # You can add more arguments in the future as needed

    return parser.parse_args()


def validate_config(config):
    """
    Validates the provided configuration dictionary to ensure all required keys and values are present.

    :param config: The configuration dictionary to validate.
    :raise ValueError: If a required key or value is missing.
    """

    # List of required keys for each section of the config
    required_keys = {
        'settings': ['logLevel', 'httpPort'],
        'config': ['apiToken', 'regionURL', 'postureAPIEndpoint', 'noDataThresholdHours']
    }

    for section, keys in required_keys.items():
        if section not in config:
            raise ValueError(f"Missing section in config: {section}")

        for key in keys:
            if key not in config[section]:
                raise ValueError(f"Missing key in {section}: {key}")
            if not config[section][key]:  # This checks for empty string or None values
                raise ValueError(f"Value for {key} in {section} is not provided or empty.")


class Collector(object):
    def __init__(self, config, json_data, hours_threshold=24):
        self.config = config
        self.data = json_data
        # Convert days to seconds
        self.timeframe_seconds = hours_threshold * 60 * 60

    @staticmethod
    def get_youngest_date(requirements_history):
        """
        Returns the most recent date from the provided requirements history.

        :param requirements_history: List of requirements with their respective dates.
        :return: The most recent date as an integer.
        """
        return max([int(rh['date']) for rh in requirements_history])

    def collect(self):
        """
        Collects and processes metrics from the Sysdig API data.

        This method fetches the required metrics from the internal data, processes them,
        and prepares them for exposure to Prometheus.

        :yield: Processed metric data suitable for Prometheus.
        """
        logging.info(f"Starting Collection Run...")
        current_timestamp = time.time()

        g_passing_requirements = GaugeMetricFamily(
            "sysdig_posture_passing_requirements",
            "Number of passing requirements",
            labels=["zone", "policy"]
        )

        g_failed_requirements = GaugeMetricFamily(
            "sysdig_posture_failed_requirements",
            "Number of failed requirements",
            labels=["zone", "policy"]
        )

        g_evaluated_resources = GaugeMetricFamily(
            "sysdig_posture_evaluated_resources",
            "Number of evaluated resources",
            labels=["zone", "policy"]
        )

        g_failed_controls = GaugeMetricFamily(
            "sysdig_posture_failed_controls",
            "Number of failed controls",
            labels=["zone", "policy"]
        )

        g_high_severity = GaugeMetricFamily(
            "sysdig_posture_high_severity_violations_resource",
            "Number of high severity resource violations",
            labels=["zone", "policy"]
        )

        g_medium_severity = GaugeMetricFamily(
            "sysdig_posture_medium_severity_violations_resource",
            "Number of medium severity resource violations",
            labels=["zone", "policy"]
        )

        g_low_severity = GaugeMetricFamily(
            "sysdig_posture_low_severity_violations_resource",
            "Number of low severity resource violations",
            labels=["zone", "policy"]
        )

        for zone_data in self.data['data']:
            for policy_data in zone_data['policies']:
                latest_date = self.get_youngest_date(policy_data['requirementsHistory'])
                if current_timestamp - latest_date <= self.timeframe_seconds:
                    g_passing_requirements.add_metric(
                        [zone_data['zoneName'], policy_data['name']], policy_data['requirementsHistory'][-1]['requirementPassingScore']
                    )
                    g_failed_requirements.add_metric(
                        [zone_data['zoneName'], policy_data['name']], policy_data['requirementsHistory'][-1]['failedRequirements']
                    )
                    g_evaluated_resources.add_metric(
                        [zone_data['zoneName'], policy_data['name']], policy_data['requirementsHistory'][-1]['evaluatedResources']
                    )
                    g_failed_controls.add_metric(
                        [zone_data['zoneName'], policy_data['name']], policy_data['failedControls']
                    )
                    g_high_severity.add_metric(
                        [zone_data['zoneName'], policy_data['name']], policy_data['resourceViolationSummary']['highSeverity']
                    )
                    g_medium_severity.add_metric(
                        [zone_data['zoneName'], policy_data['name']], policy_data['resourceViolationSummary']['mediumSeverity']
                    )
                    g_low_severity.add_metric(
                        [zone_data['zoneName'], policy_data['name']], policy_data['resourceViolationSummary']['lowSeverity']
                    )

        yield g_passing_requirements
        yield g_failed_requirements
        yield g_evaluated_resources
        yield g_failed_controls
        yield g_high_severity
        yield g_medium_severity
        yield g_low_severity


def sysdig_request(method, url, headers, params=None, _json=None, max_retries=3, base_delay=5, max_delay=60) -> requests.Response:
    """
    This module provides functionality to fetch data from the Sysdig API, and returns the results.
    It will also handle 429 Too Many Requests and other transient errors by retrying the request.
    """
    retries = 0
    response = requests.Response
    while retries <= max_retries:
        try:
            response = requests.request(method=method, url=url, headers=headers, params=params, json=_json)
            response.raise_for_status()
            return response

        except requests.exceptions.RequestException as e:
            # Handle specific exceptions as needed
            if response.status_code == 429 or isinstance(e, requests.exceptions.Timeout):
                delay = min(base_delay * (2 ** retries), max_delay)
                logging.warning(f"Error {e}. Retrying in {delay} seconds...")
                time.sleep(delay)
                retries += 1
            else:
                logging.error(" ERROR ".center(80, "-"))
                logging.error(f"Error making request to {url}: {e}")
                break

    logging.error(f"Failed to fetch data from {url} after {max_retries} retries.")
    exit(1)


if __name__ == '__main__':
    args = parse_arguments()
    with open(args.config, 'r') as file:
        obj_config = yaml.safe_load(file)

    # Validate the loaded configuration
    validate_config(obj_config)

    logging_level = obj_config['settings']['logLevel']
    logging.basicConfig(level=getattr(logging, logging_level),
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    logging.info(f"Loading Yaml Config File: {args.config}")
    auth_header['Authorization'] = f"Bearer {obj_config['config']['apiToken']}"
    data = sysdig_request(method='GET',
                          url=urljoin(base=obj_config['config']['regionURL'],
                                      url=obj_config['config']['postureAPIEndpoint']),
                          headers=auth_header)

    # Create and register custom collector
    custom_collector = Collector(config=obj_config,
                                 json_data=data.json(),
                                 hours_threshold=obj_config['config']['noDataThresholdHours'])

    REGISTRY.register(custom_collector)

    logging.info(f"Starting Prometheus HTTP Server")

    # Start the Prometheus HTTP server
    start_http_server(obj_config['settings']['httpPort'])

    # Infinite loop to keep the program running
    while True:
        time.sleep(10)  # Sleeping for 10 seconds to keep program running and not waste CPU cycles
