"""
Collects and exposes Sysdig metrics for Prometheus.

Usage:
    python script_name.py -c /path/to/config.yaml
"""
import json
import logging
import time
import requests
import yaml
import argparse
import datetime
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
    def __init__(self, config, hours_threshold=24):
        self.config = config
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

        fetchStart = datetime.datetime.now()
        json_data = sysdig_request(method='GET',
                                   url=urljoin(base=obj_config['config']['regionURL'],
                                               url=obj_config['config']['postureAPIEndpoint']),
                                   headers=auth_header).json()
        # json_data = open(file='./cspm_response.json', mode='r').read()
        # json_data = json.loads(json_data)
        fetchEnd = datetime.datetime.now()
        logging.info(f"Fetch Start: {fetchStart}, Fetch End: {fetchEnd}")
        logging.debug(f"Json Data Payload: {json_data}")
        current_timestamp = time.time()
        logging.debug('Setting up Gauge Variables begin()')
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

        g_passing_resources = GaugeMetricFamily(
            "sysdig_posture_passing_resources",
            "Number of passing resources",
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
        logging.debug('Setting up Gauge Variables end()')

        for zone_data in json_data['data']:
            for policy_data in zone_data['policies']:
                # Get the youngest date to determine if it meets our hour/time policy
                youngest_date = self.get_youngest_date(policy_data['requirementsHistory'])
                youngest_data = None

                # Find the requirement that has the youngest date and just process that
                for requirement in policy_data['requirementsHistory']:
                    if requirement['date'] == str(youngest_date):
                        youngest_data = requirement
                        logging.debug(f"Youngest Data: {requirement}")
                        break

                if current_timestamp - youngest_date <= self.timeframe_seconds:
                    g_passing_requirements.add_metric(
                        [zone_data['zoneName'], policy_data['name']],
                        youngest_data['requirementPassingScore'])
                    logging.debug(f"Adding Metric: {zone_data['zoneName'], policy_data['name']}, Data (requirementPassingScore): {youngest_data['requirementPassingScore']}")

                    g_failed_requirements.add_metric(
                        [zone_data['zoneName'], policy_data['name']],
                        youngest_data['failedRequirements'])
                    logging.debug(f"Adding Metric: {zone_data['zoneName'], policy_data['name']}, Data (failedRequirements): {youngest_data['failedRequirements']}")

                    g_evaluated_resources.add_metric(
                        [zone_data['zoneName'], policy_data['name']],
                        youngest_data['evaluatedResources'])
                    logging.debug(f"Adding Metric: {zone_data['zoneName'], policy_data['name']}, Data (evaluatedResources): {youngest_data['evaluatedResources']}")

                    g_failed_controls.add_metric(
                        [zone_data['zoneName'], policy_data['name']], policy_data['failedControls'])
                    logging.debug(f"Adding Metric: {zone_data['zoneName'], policy_data['name']}, Data (failedControls): {policy_data['failedControls']}")

                    g_passing_resources.add_metric(
                        [zone_data['zoneName'], policy_data['name']], policy_data['resourcePassingScore'])
                    logging.debug(f"Adding Metric: {zone_data['zoneName'], policy_data['name']}, Data (resourcePassingScore): {policy_data['resourcePassingScore']}")

                    g_high_severity.add_metric(
                        [zone_data['zoneName'], policy_data['name']],
                        policy_data['resourceViolationSummary']['highSeverity'])
                    logging.debug(f"Adding Metric: {zone_data['zoneName'], policy_data['name']}, Data (highSeverity): {policy_data['resourceViolationSummary']['highSeverity']}")

                    g_medium_severity.add_metric(
                        [zone_data['zoneName'], policy_data['name']],
                        policy_data['resourceViolationSummary']['mediumSeverity'])
                    logging.debug(f"Adding Metric: {zone_data['zoneName'], policy_data['name']}, Data (mediumSeverity): {policy_data['resourceViolationSummary']['mediumSeverity']}")

                    g_low_severity.add_metric(
                        [zone_data['zoneName'], policy_data['name']],
                        policy_data['resourceViolationSummary']['lowSeverity'])
                    logging.debug(f"Adding Metric: {zone_data['zoneName'], policy_data['name']}, Data (lowSeverity): {policy_data['resourceViolationSummary']['lowSeverity']}")
        logging.debug('Yielding Gauges begin()')
        yield g_passing_requirements
        yield g_failed_requirements
        yield g_evaluated_resources
        yield g_failed_controls
        yield g_passing_resources
        yield g_high_severity
        yield g_medium_severity
        yield g_low_severity
        logging.debug('Yielding Gauges end()')


def sysdig_request(method, url, headers, params=None, _json=None, max_retries=5, base_delay=5,
                   max_delay=60, timeout=10) -> requests.Response:
    """
    This module provides functionality to fetch data from the Sysdig API, and returns the results.
    It will also handle 429 Too Many Requests and other transient errors by retrying the request.
    """
    retries = 0
    e = None
    response = requests.Response()
    while retries <= max_retries:
        try:
            response = requests.request(method=method, url=url, headers=headers, params=params, json=_json, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            delay = min(base_delay * (2 ** retries), max_delay)
            logging.warning(f"Error {e}. Retrying in {delay} seconds...")
            logging.warning(f"Retry {retries}, Sleeping for {delay} seconds")
            time.sleep(delay)
            retries += 1
    logging.error(" ERROR ".center(80, "-"))
    logging.error(f"Failed to fetch data from {url} after {max_retries} retries.")
    logging.error(f"Error making request to {url}: {e}")
    response.status_code = 503  # Service is unavailable
    response._content = b"Service is unavailable after retries."
    return response


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

    # Create and register custom collector
    custom_collector = Collector(config=obj_config,
                                 hours_threshold=obj_config['config']['noDataThresholdHours'])
    logging.debug('Registering custom collector')
    REGISTRY.register(custom_collector)

    logging.info(f"Starting Prometheus HTTP Server on port {obj_config['settings']['httpPort']}")
    # Start the Prometheus HTTP server
    start_http_server(obj_config['settings']['httpPort'])
    logging.info(f"Started Prometheus HTTP Server on port {obj_config['settings']['httpPort']}")

    # Infinite loop to keep the program running
    while True:
        time.sleep(10)  # Sleeping for 10 seconds to keep program running and not waste CPU cycles
