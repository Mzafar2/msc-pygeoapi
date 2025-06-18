# =================================================================
#
# Author:
#
# Copyright (c)
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================

import re
import time
import pytest
import requests
import yaml
import jsonschema
from jsonschema import ValidationError, validate
from jsonschema import Draft202012Validator
from jsonschema import exceptions
from referencing import Registry, Resource, jsonschema
from parse import parse
from datetime import datetime, date
import json
import os

# Variables for storing collection test elapsed time
NIGHLTY_SERVICE_ONLINE_TIME = 0
NIGHLTY_DATE_TIME = 0
COVERAGE_COLLECTION_ROOT_TIME = 0
COVERAGE_COLLECTION_SCHEMA_TIME = 0
COVERAGE_COLLECTION_COV_RESPONSE_TIME = 0
FEATURE_COLLECTION_SINGLE_ITEM_TIME = 0
FEATURE_COLLECTION_ITEMS_TIME = 0
FEATURE_COLLECTION_ROOT_TIME = 0
COVERAGE_COLLECTION_VARIABLE_PROPERTY_TIME = 0
COVERAGE_COLLECTION_EXTENTS_TIME = 0
PROCESS_COLLECTION_ROOT_TIME = 0
PROCESS_COLLECTION_EXECUTE_TIME = 0

# Test summary dictionary
TEST_SUMMARY = {
    "Test Nightly Service Online": {
        "Elapsed Time": 0,
        "Errors": []
    },
    "Test Nightly Date": {
        "Elapsed Time": 0,
        "Errors": []
    },
    "Test Feature Collection Single Item": {
        "Elapsed Time": 0,
        "Errors": []
    },
    "Test Feature Collection Items": {
        "Elapsed Time": 0,
        "Errors": []
    },
    "Test Feature Collection Root": {
        "Elapsed Time": 0,
        "Errors": []
    },
    "Test Coverage Collection Root": {
        "Elapsed Time": 0,
        "Errors": []
    },
    "Test Coverage Collection Schema": {
        "Elapsed Time": 0,
        "Errors": []
    },
    "Test Coverage Collection Coverage Response": {
        "Elapsed Time": 0,
        "Errors": []
    },
    "Test Coverage Collection Variable Property": {
        "Elapsed Time": 0,
        "Errors": []
    },
    "Test Coverage Collection Extents": {
        "Elapsed Time": 0,
        "Errors": []
    },
    "Test Process Collection Root": {
        "Elapsed Time": 0,
        "Errors": []
    },
    "Test Process Collection Execute": {
        "Elapsed Time": 0,
        "Errors": []
    }
}


@pytest.fixture(scope='session', autouse=True)
def run_before_and_after_tests():
    print('before test')

    yield

    print(json.dumps(TEST_SUMMARY, indent=4))

    # Write test summary dictionary to a JSON file after all tests are complete
    with open("tests/test-files/test_summary.json", "w") as f:
        json.dump(TEST_SUMMARY, f, indent=4)


# Setup helper functions below

# Validate coverage response
def helper_coverage_response_validation(url):
    """
    Validate the CovJSON given by the url and return any errors.

    Parameters:
    url (string): Endpoint to test.

    Returns:

    dict: A dictionary with two keys:
        - 'error_messages' (list of str): List of formatted error message strings.
        - 'error_info' (list of dict): List of error details as dictionaries,
          including 'collectionId', 'url', 'errorType', and 'statusCode'.
    """

    global TEST_SUMMARY
    collection_id = url.split('/collections/')[1].split('?')[0]

    response = requests.get(url, verify="/etc/ssl/certs")

    try:
        assert response.status_code == 200
    except AssertionError:
        error_info = {
                'collectionId': collection_id,
                'url': url,
                'errorType': 'Status Code Error',
                'statusCode': response.status_code
        }

        error_message = (
                f"\n\ncollectionId: {collection_id}\n"
                f"url: {url}\n"
                f"errorType: Status Code Error\n"
                f"statusCode: {response.status_code}\n"
            )

        return {'error_messages': [error_message], 'error_info': [error_info]}

    instance = response.json()

    # Define the base directory
    base_dir = os.path.abspath('tests/test-files/schemasCov')

    # Load the collection.yaml file
    schema_a_path = os.path.join(base_dir, 'coverage.json')
    with open(schema_a_path, 'r') as f:
        schema_a = json.load(f)

    # resource for schema a
    resourceA = Resource(contents=schema_a, specification=jsonschema.DRAFT202012)

    registry = Registry().with_resources([(f'{base_dir}', resourceA)])

    # Register the schema a in the registry as a resource
    registry = registry.crawl()

    validator = Draft202012Validator(schema_a, registry=registry)

    # Collect all errors
    errors = list(validator.iter_errors(instance))

    output = helper_validation_error_message(errors, url, collection_id)

    return output


def helper_validation_error_message(errors, url, collectionId):
    """
    Generate a structured summary of validation errors for a given dataset.

    Parameters:
    errors (list): A list of validation error objects.
    url (str): The URL of the resource being validated.
    collectionId (str): Identifier for the collection the resource belongs to.

    Returns:
    dict: A dictionary containing:
        - 'error_messages' (list of str): Human-readable, detailed error messages for logging or reporting.
        - 'error_info' (list of dict): Structured error metadata with keys:
            - 'collectionId' (str): The ID of the data collection.
            - 'url' (str): The URL that was validated.
            - 'errorType' (str): Type of error (always 'Validation Error').
            - 'failedSchemaItem' (str): Path in the schema where validation failed.
            - 'failedInstanceItem' (str): Path in the instance (input) that failed validation.
            - 'errorMessage' (str): The error message from the validator.
    """

    output = {'error_messages': [], 'error_info': []}

    if errors:
        # Build a detailed error message that includes schema and instance paths
        error_messages = []
        for error in errors:
            # Format the schema path (this is where the validation failed)
            schema_path = " -> ".join(str(p) for p in error.absolute_schema_path)
            # Format the instance path (this is where the error occurred in the instance)
            instance_path = " -> ".join(str(p) for p in error.absolute_path)


            #  detailed error message
            error_message = (
                f"\n\nFailed validating '{error.validator}' in schema path: {schema_path}\n"
                f"On instance path: {instance_path}\n"
                f"Schema: {error.schema}\n"
                f"Instance: {error.instance}\n"
                f"Message: {error.message}"
            )
            error_messages.append(error_message)
            output['error_messages'].append(error_message)

            # Fill test summary dict

            error_info = {
                'collectionId': collectionId,
                'url': url,
                'errorType': 'Validation Error',
                'failedSchemaItem': schema_path,
                'failedInstanceItem': instance_path,
                'errorMessage': error.message
            }
            output['error_info'].append(error_info)

    return output



def get_feature_collection_root_urls():
    """
    Retrieve the root URLs for all feature collections from the GeoMet API.

    Returns:
    list of str: A list of URLs for feature collections.
    """

    url = 'https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections?f=json'
    urlList = []

    response = requests.get(url, verify="/etc/ssl/certs")

    instance = response.json()

    assert response.status_code == 200

    for collection in instance['collections']:
        if 'itemType' in collection and collection['itemType'] == 'feature':
            urlToAdd = f"https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections/{collection['id']}?f=json"
            urlList.append(urlToAdd)

    return urlList


def get_feature_collection_items_urls():
    """
    Retrieve the 'items' URLs for all feature collections from the GeoMet API.

    Returns:
    list of str: A list of 'items' URLs for coverage collections.
    """

    url = 'https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections?f=json'
    urlList = []

    response = requests.get(url, verify="/etc/ssl/certs")

    instance = response.json()

    assert response.status_code == 200

    for collection in instance['collections']:
        if 'itemType' in collection and collection['itemType'] == 'feature':
            urlToAdd = 'https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections/' + collection['id'] + '/items?limit=1&f=json'
            urlList.append(urlToAdd)

    return urlList


def get_feature_collection_single_items_urls():
    """
    Retrieve the 'single item' URLs for all feature collections from the GeoMet API.

    Returns:
    list of str: A list of 'single item' URLs for feature collections.
    """

    url = 'https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections?f=json'
    urlList = []

    response = requests.get(url, verify="/etc/ssl/certs")

    instance = response.json()

    assert response.status_code == 200

    for collection in instance['collections']:
        if 'itemType' in collection and collection['itemType'] == 'feature':
            requestUrl = f"https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections/{collection['id']}/items?limit=1&f=json"

            try:
                response2 = requests.get(requestUrl, verify="/etc/ssl/certs")
                assert response2.status_code == 200

                instance2 = response2.json()
                itemId = instance2['features'][0]['id']
                urlToAdd = f"https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections/{collection['id']}/items/{itemId}?f=json"
                urlList.append(urlToAdd)

            except Exception as e:
                print(f"Error {e}: Could not request items for {collection['id']}")

    return urlList

def get_coverage_collection_root_urls():
    """
    Retrieve the root URLs for all coverage collections from the GeoMet API.

    Returns:
    list of str: A list of root URLs for coverage collections.
    """

    url = 'https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections?f=json'
    urlList = []
    response = requests.get(url, verify="/etc/ssl/certs")

    instance = response.json()

    assert response.status_code == 200

    for collection in instance['collections']:
        if 'itemType' not in collection:
            urlToAdd = f"https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections/{collection['id']}?f=json"
            urlList.append(urlToAdd)

    return urlList


def get_coverage_collection_schema_urls():
    """
    Retrieve the 'schema' URLs for all coverage collections from the GeoMet API.

    Returns:
    list of str: A list of 'schema' URLs for coverage collections.
    """

    url = 'https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections?f=json'
    urlList = []
    response = requests.get(url, verify="/etc/ssl/certs")

    instance = response.json()

    assert response.status_code == 200

    for collection in instance['collections']:
        if 'itemType' not in collection:
            urlToAdd = f"https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections/{collection['id']}/schema?f=json"
            urlList.append(urlToAdd)

    return urlList


def get_coverage_collection_coverageData_urls():
    """
    Retrieve the 'coverage data' URLs for all coverage collections from the GeoMet API.

    Returns:
    list of str: A list of 'coverage data' URLs for coverage collections.
    """

    url = 'https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections?f=json'
    urlList = []
    response = requests.get(url, verify="/etc/ssl/certs")

    instance = response.json()

    assert response.status_code == 200

    for collection in instance['collections']:
        if 'itemType' not in collection:
            urlToAdd = f"https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections/{collection['id']}/coverage?f=json"
            urlList.append(urlToAdd)

    return urlList

def get_process_urls():
    """
    Retrieve the 'processes' URLs for all processes collections from the GeoMet API.

    Returns:
    list of str: A list of 'processes' URLs for processes collections.
    """

    url = 'https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/processes?f=json'
    urlList = []
    response = requests.get(url, verify="/etc/ssl/certs")

    instance = response.json()

    assert response.status_code == 200

    for process in instance['processes']:
        urlToAdd = f"https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/processes/{process['id']}?f=json"
        urlList.append(urlToAdd)

    return urlList

def get_process_execution_urls():
    """
    Retrieve the 'execution' URLs for all processes collections from the GeoMet API.

    Returns:
    list of str: A list of 'execution' URLs for processes collections.
    """

    url = 'https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/processes?f=json'
    urlList = []
    response = requests.get(url, verify="/etc/ssl/certs")

    instance = response.json()

    assert response.status_code == 200

    for process in instance['processes']:
        urlToAdd = f"https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/processes/{process['id']}/execution?f=json"
        urlList.append(urlToAdd)

    return urlList


# Setup variables storing URL lists to pass as arguments during the testing below

featureCollectionRootUrlList = get_feature_collection_root_urls()
featureCollectionItemsUrlList = get_feature_collection_items_urls()
featureCollectionSingleItemsUrlList = get_feature_collection_single_items_urls()
CoverageCollectionRootUrlList = get_coverage_collection_root_urls()
CoverageCollectionSchemaUrlList = get_coverage_collection_schema_urls()
coverageCollectionCoverageDataUrlList = get_coverage_collection_coverageData_urls()
processUrlList = get_process_urls()
processExecutionUrlList = get_process_execution_urls()


# Integration tests begin

def test_nightly_service_online():
    """
    Pytest function to test if the nightly is online.

    Raises:
    AssertionError: If the HTTP response status code is not 200.
    """

    url = 'https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi'

    global NIGHLTY_SERVICE_ONLINE_TIME
    global TEST_SUMMARY

    start_time = time.time()  # Capture start time

    response = requests.get(url, verify="/etc/ssl/certs")

    try:
        assert response.status_code == 200
    except AssertionError:
        error_info = {
                'url': url,
                'errorType': 'Service Down Error',
                'statusCode': response.status_code
        }

        TEST_SUMMARY['Test Nightly Service Online']['Errors'].append(error_info)

        end_time = time.time()  # Capture end time after the test has run
        elapsed_time = end_time - start_time
        NIGHLTY_SERVICE_ONLINE_TIME += elapsed_time
        TEST_SUMMARY['Test Nightly Service Online']['Elapsed Time'] = NIGHLTY_SERVICE_ONLINE_TIME

        raise

def test_nightly_date():
    """
    Test if latest nightly build matches today's date
    """
    global NIGHLTY_DATE_TIME
    global TEST_SUMMARY

    start_time = time.time()  # Capture start time

    # retrieve name of directory the latest symbolic link is pointing to
    latest = os.path.basename(
        os.path.realpath('/data/web/msc-pygeoapi-nightly/latest')
    )

    # parse date from directory name
    latest_parsed = parse('msc-pygeoapi-{YYYYMMDD}.{HHMM}', latest)
    latest_date = datetime.strptime(
        latest_parsed['YYYYMMDD'],
        '%Y%m%d'
    ).date()

    # assert parsed date is equal to today's date
    try:
        assert latest_date == date.today()
    except AssertionError:
        error_info = {
                'errorType': 'File Date Mismatch Error',
                'errorMessage': f"Nightly build date ({latest_date}) does not match today's date ({date.today()})."
        }

        TEST_SUMMARY['Test Nightly Date']['Errors'].append(error_info)

        end_time = time.time()  # Capture end time after the test has run
        elapsed_time = end_time - start_time
        NIGHLTY_DATE_TIME += elapsed_time
        TEST_SUMMARY['Test Nightly Date']['Elapsed Time'] = NIGHLTY_DATE_TIME
        raise AssertionError(
            f"Nightly build date ({latest_date}) does not match today's date ({date.today()})."
        )

@pytest.mark.parametrize("url", featureCollectionRootUrlList)
def test_feature_collection_root(url):
    """
    Pytest function to validate the structure and content of a GeoMet Feature Collection root JSON response.

    This test performs the following for each URL in `featureCollectionRootUrlList`:
    - Sends a GET request to the specified feature collection URL.
    - Asserts that the response has a 200 OK status.
    - Loads the JSON response and validates it against a set of predefined JSON Schemas
    - Uses a schema registry to resolve internal schema references.
    - Collects and reports validation errors with detailed messages and context.
    - Updates a global `TEST_SUMMARY` object with error details and elapsed test time.

    Parameters:
    url (str): The feature collection metadata URL to validate.

    Raises:
    AssertionError: If the HTTP response status code is not 200.
    ValidationError: If the JSON does not conform to the expected schema(s).
    """

    # test with url: https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections/climate-normals?f=json
    # url = 'https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections/climate-normals?f=json'
    global FEATURE_COLLECTION_ROOT_TIME
    global TEST_SUMMARY
    collection_id = url.split('/collections/')[1].split('?')[0]

    start_time = time.time()  # Capture start time

    response = requests.get(url, verify="/etc/ssl/certs")

    instance = response.json()

    try:
        assert response.status_code == 200
    except AssertionError:
        error_info = {
                'collectionId': collection_id,
                'url': url,
                'errorType': 'Status Code Error',
                'statusCode': response.status_code
        }

        TEST_SUMMARY['Test Feature Collection Root']['Errors'].append(error_info)

        end_time = time.time()  # Capture end time after the test has run
        elapsed_time = end_time - start_time
        FEATURE_COLLECTION_ROOT_TIME += elapsed_time
        TEST_SUMMARY['Test Feature Collection Root']['Elapsed Time'] = FEATURE_COLLECTION_ROOT_TIME

        raise

    # Define the base directory
    base_dir = os.path.abspath('tests/test-files/schemasFeat')

    # Load the collection.yaml file
    schema_a_path = os.path.join(base_dir, 'collection.yaml')
    with open(schema_a_path, 'r') as f:
        schema_a = yaml.safe_load(f)

    # Load the other extent.yaml file
    schema_b_path = os.path.join(base_dir, 'extent.yaml')
    with open(schema_b_path, 'r') as f:
        schema_b = yaml.safe_load(f)

    # Load the other link.yaml file
    schema_c_path = os.path.join(base_dir, 'link.yaml')
    with open(schema_c_path, 'r') as f:
        schema_c = yaml.safe_load(f)

    # Load the other linkBase.yaml file
    schema_d_path = os.path.join(base_dir, 'linkBase.yaml')
    with open(schema_d_path, 'r') as f:
        schema_d = yaml.safe_load(f)

    # Load the other linkTemplate.yaml file
    schema_e_path = os.path.join(base_dir, 'linkTemplate.yaml')
    with open(schema_e_path, 'r') as f:
        schema_e = yaml.safe_load(f)


    # resource for schema a
    resourceA = Resource(contents=schema_a, specification=jsonschema.DRAFT202012)
    # resource for schema b
    resourceB = Resource(contents=schema_b, specification=jsonschema.DRAFT202012)
    # resource for schema c
    resourceC = Resource(contents=schema_c, specification=jsonschema.DRAFT202012)
    # resource for schema d
    resourceD = Resource(contents=schema_d, specification=jsonschema.DRAFT202012)
    # resource for schema e
    resourceE = Resource(contents=schema_e, specification=jsonschema.DRAFT202012)

    registry = Registry().with_resources([(f'{base_dir}', resourceA), ('extent.yaml', resourceB), ('link.yaml', resourceC), ('linkBase.yaml', resourceD), ('linkTemplate.yaml', resourceE)])

    # Register the schema a in the registry as a resource
    # registry = Registry().with_resource(uri=f'file://{base_dir}/', resource=resource)
    registry = registry.crawl()

    validator = Draft202012Validator(schema_a, registry=registry)
    # validator.validate(instance)

    # Collect all errors
    errors = list(validator.iter_errors(instance))

    output = helper_validation_error_message(errors, url, collection_id)

    if output['error_messages'] and output['error_info']:

        TEST_SUMMARY['Test Feature Collection Root']['Errors'] += output['error_info']

        end_time = time.time()  # Capture end time after the test has run
        elapsed_time = end_time - start_time
        FEATURE_COLLECTION_ROOT_TIME += elapsed_time
        TEST_SUMMARY['Test Feature Collection Root']['Elapsed Time'] = FEATURE_COLLECTION_ROOT_TIME

        # Raise a ValidationError with all error messages
        raise ValidationError("\n\n".join(output['error_messages']))
    else:
        print("Instance is valid.")

        end_time = time.time()  # Capture end time after the test has run
        elapsed_time = end_time - start_time
        FEATURE_COLLECTION_ROOT_TIME += elapsed_time
        TEST_SUMMARY['Test Feature Collection Root']['Elapsed Time'] = FEATURE_COLLECTION_ROOT_TIME

@pytest.mark.parametrize("url", featureCollectionItemsUrlList)
def test_feature_collection_items(url):
    """
    Pytest function to validate the structure and content of GeoMet Feature Collection items JSON response.

    This test performs the following for each URL in `featureCollectionItemsUrlList`:
    - Sends a GET request to the specified feature collection URL.
    - Asserts that the response has a 200 OK status.
    - Loads the JSON response and validates it against a set of predefined JSON Schemas
    - Uses a schema registry to resolve internal schema references.
    - Collects and reports validation errors with detailed messages and context.
    - Updates a global `TEST_SUMMARY` object with error details and elapsed test time.

    Parameters:
    url (str): The feature collection metadata URL to validate.

    Raises:
    AssertionError: If the HTTP response status code is not 200.
    ValidationError: If the JSON does not conform to the expected schema(s).
    """

    # test with url: https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections/climate-normals/items?limit=1&f=json

    global FEATURE_COLLECTION_ITEMS_TIME
    global TEST_SUMMARY
    collection_id = url.split('/collections/')[1].split('?')[0]

    start_time = time.time()  # Capture start time

    response = requests.get(url, verify="/etc/ssl/certs")

    instance = response.json()

    # assert response.status_code == 200
    try:
        assert response.status_code == 200
    except AssertionError:
        error_info = {
                'collectionId': collection_id,
                'url': url,
                'errorType': 'Status Code Error',
                'statusCode': response.status_code
        }

        TEST_SUMMARY['Test Feature Collection Items']['Errors'].append(error_info)

        end_time = time.time()  # Capture end time after the test has run
        elapsed_time = end_time - start_time
        FEATURE_COLLECTION_ITEMS_TIME += elapsed_time
        TEST_SUMMARY['Test Feature Collection Items']['Elapsed Time'] = FEATURE_COLLECTION_ITEMS_TIME

        raise


    # Define the base directory
    base_dir = os.path.abspath('tests/test-files/schemasFeat')

    # Load the featureCollectionGeoJSON.yaml file
    schema_a_path = os.path.join(base_dir, 'featureCollectionGeoJSON.yaml')
    with open(schema_a_path, 'r') as f:
        schema_a = yaml.safe_load(f)

    # Load the other featureGeoJSON.yaml file
    schema_b_path = os.path.join(base_dir, 'featureGeoJSON.yaml')
    with open(schema_b_path, 'r') as f:
        schema_b = yaml.safe_load(f)

    # Load the other link.yaml file
    schema_c_path = os.path.join(base_dir, 'link.yaml')
    with open(schema_c_path, 'r') as f:
        schema_c = yaml.safe_load(f)

    # Load the other linkBase.yaml file
    schema_d_path = os.path.join(base_dir, 'linkBase.yaml')
    with open(schema_d_path, 'r') as f:
        schema_d = yaml.safe_load(f)

    # Load the other geometryGeoJSON.yaml file
    schema_e_path = os.path.join(base_dir, 'geometryGeoJSON.yaml')
    with open(schema_e_path, 'r') as f:
        schema_e = yaml.safe_load(f)

        # Load the other pointGeoJSON.yaml file
    schema_f_path = os.path.join(base_dir, 'pointGeoJSON.yaml')
    with open(schema_f_path, 'r') as f:
        schema_f = yaml.safe_load(f)

        # Load the other multipointGeoJSON.yaml file
    schema_g_path = os.path.join(base_dir, 'multipointGeoJSON.yaml')
    with open(schema_g_path, 'r') as f:
        schema_g = yaml.safe_load(f)

        # Load the other linestringGeoJSON.yaml file
    schema_h_path = os.path.join(base_dir, 'linestringGeoJSON.yaml')
    with open(schema_h_path, 'r') as f:
        schema_h = yaml.safe_load(f)

        # Load the other multilinestringGeoJSON.yaml file
    schema_i_path = os.path.join(base_dir, 'multilinestringGeoJSON.yaml')
    with open(schema_i_path, 'r') as f:
        schema_i = yaml.safe_load(f)

        # Load the other polygonGeoJSON.yaml file
    schema_j_path = os.path.join(base_dir, 'polygonGeoJSON.yaml')
    with open(schema_j_path, 'r') as f:
        schema_j = yaml.safe_load(f)

        # Load the other multipolygonGeoJSON.yaml file
    schema_k_path = os.path.join(base_dir, 'multipolygonGeoJSON.yaml')
    with open(schema_k_path, 'r') as f:
        schema_k = yaml.safe_load(f)

        # Load the other geometrycollectionGeoJSON.yaml file
    schema_l_path = os.path.join(base_dir, 'geometrycollectionGeoJSON.yaml')
    with open(schema_l_path, 'r') as f:
        schema_l = yaml.safe_load(f)


    # resource for schema a
    resourceA = Resource(contents=schema_a, specification=jsonschema.DRAFT202012)
    # resource for schema b
    resourceB = Resource(contents=schema_b, specification=jsonschema.DRAFT202012)
    # resource for schema c
    resourceC = Resource(contents=schema_c, specification=jsonschema.DRAFT202012)
    # resource for schema d
    resourceD = Resource(contents=schema_d, specification=jsonschema.DRAFT202012)
    # resource for schema e
    resourceE = Resource(contents=schema_e, specification=jsonschema.DRAFT202012)
    # resource for schema f
    resourceF = Resource(contents=schema_f, specification=jsonschema.DRAFT202012)
    # resource for schema g
    resourceG = Resource(contents=schema_g, specification=jsonschema.DRAFT202012)
    # resource for schema h
    resourceH = Resource(contents=schema_h, specification=jsonschema.DRAFT202012)
    # resource for schema i
    resourceI = Resource(contents=schema_i, specification=jsonschema.DRAFT202012)
    # resource for schema j
    resourceJ = Resource(contents=schema_j, specification=jsonschema.DRAFT202012)
    # resource for schema k
    resourceK = Resource(contents=schema_k, specification=jsonschema.DRAFT202012)
    # resource for schema l
    resourceL = Resource(contents=schema_l, specification=jsonschema.DRAFT202012)

    registry = Registry().with_resources([(f'{base_dir}', resourceA), ('featureGeoJSON.yaml', resourceB), ('link.yaml', resourceC), ('linkBase.yaml', resourceD), ('geometryGeoJSON.yaml', resourceE), ('pointGeoJSON.yaml', resourceF), ('multipointGeoJSON.yaml', resourceG), ('linestringGeoJSON.yaml', resourceH), ('multilinestringGeoJSON.yaml', resourceI), ('polygonGeoJSON.yaml', resourceJ), ('multipolygonGeoJSON.yaml', resourceK), ('geometrycollectionGeoJSON.yaml', resourceL)])

    # Register the schema a in the registry as a resource
    registry = registry.crawl()

    validator = Draft202012Validator(schema_a, registry=registry)
    # validator.validate(instance)

    # Collect all errors
    errors = list(validator.iter_errors(instance))

    output = helper_validation_error_message(errors, url, collection_id)

    if output['error_messages'] and output['error_info']:

        TEST_SUMMARY['Test Feature Collection Items']['Errors'] += output['error_info']

        end_time = time.time()  # Capture end time after the test has run
        elapsed_time = end_time - start_time
        FEATURE_COLLECTION_ITEMS_TIME += elapsed_time
        TEST_SUMMARY['Test Feature Collection Items']['Elapsed Time'] = FEATURE_COLLECTION_ITEMS_TIME

        # Raise a ValidationError with all error messages
        raise ValidationError("\n\n".join(output['error_messages']))
    else:
        print("Instance is valid.")

        end_time = time.time()  # Capture end time after the test has run
        elapsed_time = end_time - start_time
        FEATURE_COLLECTION_ITEMS_TIME += elapsed_time
        TEST_SUMMARY['Test Feature Collection Items']['Elapsed Time'] = FEATURE_COLLECTION_ITEMS_TIME


@pytest.mark.parametrize("url", featureCollectionSingleItemsUrlList)
def test_feature_collection_single_item(url):
    """
    Pytest function to validate the structure and content of GeoMet Feature Collection single item JSON response.

    This test performs the following for each URL in `featureCollectionSingleItemsUrlList`:
    - Sends a GET request to the specified feature collection URL.
    - Asserts that the response has a 200 OK status.
    - Loads the JSON response and validates it against a set of predefined JSON Schemas
    - Uses a schema registry to resolve internal schema references.
    - Collects and reports validation errors with detailed messages and context.
    - Updates a global `TEST_SUMMARY` object with error details and elapsed test time.

    Parameters:
    url (str): The feature collection metadata URL to validate.

    Raises:
    AssertionError: If the HTTP response status code is not 200.
    ValidationError: If the JSON does not conform to the expected schema(s).
    """

    # test with url: https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections/climate-normals/items/1664.62.1?f=json
    global FEATURE_COLLECTION_SINGLE_ITEM_TIME
    global TEST_SUMMARY
    collection_id = url.split('/collections/')[1].split('?')[0]

    start_time = time.time()  # Capture start time

    response = requests.get(url, verify="/etc/ssl/certs")

    instance = response.json()

    # assert response.status_code == 200
    try:
        assert response.status_code == 200
    except AssertionError:
        error_info = {
                'collectionId': collection_id,
                'url': url,
                'errorType': 'Status Code Error',
                'statusCode': response.status_code
        }

        TEST_SUMMARY['Test Feature Collection Single Item']['Errors'].append(error_info)

        end_time = time.time()  # Capture end time after the test has run
        elapsed_time = end_time - start_time
        FEATURE_COLLECTION_SINGLE_ITEM_TIME += elapsed_time
        TEST_SUMMARY['Test Feature Collection Single Item']['Elapsed Time'] = FEATURE_COLLECTION_SINGLE_ITEM_TIME

        raise

    # Define the base directory
    base_dir = os.path.abspath('tests/test-files/schemasFeat')


    # Load the other featureGeoJSON.yaml file
    schema_b_path = os.path.join(base_dir, 'featureGeoJSON.yaml')
    with open(schema_b_path, 'r') as f:
        schema_b = yaml.safe_load(f)

    # Load the other link.yaml file
    schema_c_path = os.path.join(base_dir, 'link.yaml')
    with open(schema_c_path, 'r') as f:
        schema_c = yaml.safe_load(f)

    # Load the other linkBase.yaml file
    schema_d_path = os.path.join(base_dir, 'linkBase.yaml')
    with open(schema_d_path, 'r') as f:
        schema_d = yaml.safe_load(f)

    # Load the other geometryGeoJSON.yaml file
    schema_e_path = os.path.join(base_dir, 'geometryGeoJSON.yaml')
    with open(schema_e_path, 'r') as f:
        schema_e = yaml.safe_load(f)

        # Load the other pointGeoJSON.yaml file
    schema_f_path = os.path.join(base_dir, 'pointGeoJSON.yaml')
    with open(schema_f_path, 'r') as f:
        schema_f = yaml.safe_load(f)

        # Load the other multipointGeoJSON.yaml file
    schema_g_path = os.path.join(base_dir, 'multipointGeoJSON.yaml')
    with open(schema_g_path, 'r') as f:
        schema_g = yaml.safe_load(f)

        # Load the other linestringGeoJSON.yaml file
    schema_h_path = os.path.join(base_dir, 'linestringGeoJSON.yaml')
    with open(schema_h_path, 'r') as f:
        schema_h = yaml.safe_load(f)

        # Load the other multilinestringGeoJSON.yaml file
    schema_i_path = os.path.join(base_dir, 'multilinestringGeoJSON.yaml')
    with open(schema_i_path, 'r') as f:
        schema_i = yaml.safe_load(f)

        # Load the other polygonGeoJSON.yaml file
    schema_j_path = os.path.join(base_dir, 'polygonGeoJSON.yaml')
    with open(schema_j_path, 'r') as f:
        schema_j = yaml.safe_load(f)

        # Load the other multipolygonGeoJSON.yaml file
    schema_k_path = os.path.join(base_dir, 'multipolygonGeoJSON.yaml')
    with open(schema_k_path, 'r') as f:
        schema_k = yaml.safe_load(f)

        # Load the other geometrycollectionGeoJSON.yaml file
    schema_l_path = os.path.join(base_dir, 'geometrycollectionGeoJSON.yaml')
    with open(schema_l_path, 'r') as f:
        schema_l = yaml.safe_load(f)


    # resource for schema b
    resourceB = Resource(contents=schema_b, specification=jsonschema.DRAFT202012)
    # resource for schema c
    resourceC = Resource(contents=schema_c, specification=jsonschema.DRAFT202012)
    # resource for schema d
    resourceD = Resource(contents=schema_d, specification=jsonschema.DRAFT202012)
    # resource for schema e
    resourceE = Resource(contents=schema_e, specification=jsonschema.DRAFT202012)
    # resource for schema f
    resourceF = Resource(contents=schema_f, specification=jsonschema.DRAFT202012)
    # resource for schema g
    resourceG = Resource(contents=schema_g, specification=jsonschema.DRAFT202012)
    # resource for schema h
    resourceH = Resource(contents=schema_h, specification=jsonschema.DRAFT202012)
    # resource for schema i
    resourceI = Resource(contents=schema_i, specification=jsonschema.DRAFT202012)
    # resource for schema j
    resourceJ = Resource(contents=schema_j, specification=jsonschema.DRAFT202012)
    # resource for schema k
    resourceK = Resource(contents=schema_k, specification=jsonschema.DRAFT202012)
    # resource for schema l
    resourceL = Resource(contents=schema_l, specification=jsonschema.DRAFT202012)

    registry = Registry().with_resources([('featureGeoJSON.yaml', resourceB), ('link.yaml', resourceC), ('linkBase.yaml', resourceD), ('geometryGeoJSON.yaml', resourceE), ('pointGeoJSON.yaml', resourceF), ('multipointGeoJSON.yaml', resourceG), ('linestringGeoJSON.yaml', resourceH), ('multilinestringGeoJSON.yaml', resourceI), ('polygonGeoJSON.yaml', resourceJ), ('multipolygonGeoJSON.yaml', resourceK), ('geometrycollectionGeoJSON.yaml', resourceL)])

    # Register the schema a in the registry as a resource
    registry = registry.crawl()

    validator = Draft202012Validator(schema_b, registry=registry)
    # validator.validate(instance)

    # Collect all errors
    errors = list(validator.iter_errors(instance))

    output = helper_validation_error_message(errors, url, collection_id)

    if output['error_messages'] and output['error_info']:

        TEST_SUMMARY['Test Feature Collection Single Item']['Errors'] += output['error_info']

        end_time = time.time()  # Capture end time after the test has run
        elapsed_time = end_time - start_time
        FEATURE_COLLECTION_SINGLE_ITEM_TIME += elapsed_time
        TEST_SUMMARY['Test Feature Collection Single Item']['Elapsed Time'] = FEATURE_COLLECTION_SINGLE_ITEM_TIME

        # Raise a ValidationError with all error messages
        raise ValidationError("\n\n".join(output['error_messages']))
    else:
        print("Instance is valid.")

        end_time = time.time()  # Capture end time after the test has run
        elapsed_time = end_time - start_time
        FEATURE_COLLECTION_SINGLE_ITEM_TIME += elapsed_time
        TEST_SUMMARY['Test Feature Collection Single Item']['Elapsed Time'] = FEATURE_COLLECTION_SINGLE_ITEM_TIME


@pytest.mark.parametrize("url", CoverageCollectionRootUrlList)
def test_coverage_collection_root(url):
    """
    Pytest function to validate the structure and content of GeoMet Coverage Collection root JSON response.

    This test performs the following for each URL in `CoverageCollectionRootUrlList`:
    - Sends a GET request to the specified feature collection URL.
    - Asserts that the response has a 200 OK status.
    - Loads the JSON response and validates it against a set of predefined JSON Schemas
    - Uses a schema registry to resolve internal schema references.
    - Collects and reports validation errors with detailed messages and context.
    - Updates a global `TEST_SUMMARY` object with error details and elapsed test time.

    Parameters:
    url (str): The feature collection metadata URL to validate.

    Raises:
    AssertionError: If the HTTP response status code is not 200.
    ValidationError: If the JSON does not conform to the expected schema(s).
    """
    # test with url: https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections/climate:dcs:projected:annual:P20Y-Avg?f=json

    global COVERAGE_COLLECTION_ROOT_TIME
    global TEST_SUMMARY
    collection_id = url.split('/collections/')[1].split('?')[0]

    start_time = time.time()  # Capture start time

    response = requests.get(url, verify="/etc/ssl/certs")

    instance = response.json()

    # assert response.status_code == 200
    try:
        assert response.status_code == 200
    except AssertionError:
        error_info = {
                'collectionId': collection_id,
                'url': url,
                'errorType': 'Status Code Error',
                'statusCode': response.status_code
        }

        TEST_SUMMARY['Test Coverage Collection Root']['Errors'].append(error_info)

        end_time = time.time()  # Capture end time after the test has run
        elapsed_time = end_time - start_time
        COVERAGE_COLLECTION_ROOT_TIME += elapsed_time
        TEST_SUMMARY['Test Coverage Collection Root']['Elapsed Time'] = COVERAGE_COLLECTION_ROOT_TIME

        raise

    # Define the base directory
    base_dir = os.path.abspath('tests/test-files/schemasCov')

    # Load the collection.yaml file
    schema_a_path = os.path.join(base_dir, 'common-geodata/collectionDesc.yaml')
    with open(schema_a_path, 'r') as f:
        schema_a = yaml.safe_load(f)

    # Load the other extent.yaml file
    schema_b_path = os.path.join(base_dir, 'common-geodata/extent-uad.yaml')
    with open(schema_b_path, 'r') as f:
        schema_b = yaml.safe_load(f)

    # Load the other link.yaml file
    schema_c_path = os.path.join(base_dir, 'common-core/link.yaml')
    with open(schema_c_path, 'r') as f:
        schema_c = yaml.safe_load(f)

    # Load the other linkBase.yaml file
    schema_d_path = os.path.join(base_dir, 'common-geodata/dataType.yaml')
    with open(schema_d_path, 'r') as f:
        schema_d = yaml.safe_load(f)

    # Load the other linkTemplate.yaml file
    schema_e_path = os.path.join(base_dir, 'common-geodata/extent.yaml')
    with open(schema_e_path, 'r') as f:
        schema_e = yaml.safe_load(f)


    # resource for schema a
    resourceA = Resource(contents=schema_a, specification=jsonschema.DRAFT202012)
    # resource for schema b
    resourceB = Resource(contents=schema_b, specification=jsonschema.DRAFT202012)
    # resource for schema c
    resourceC = Resource(contents=schema_c, specification=jsonschema.DRAFT202012)
    # resource for schema d
    resourceD = Resource(contents=schema_d, specification=jsonschema.DRAFT202012)
    # resource for schema e
    resourceE = Resource(contents=schema_e, specification=jsonschema.DRAFT202012)

    registry = Registry().with_resources([('/common-geodata/collectionDesc.yaml', resourceA), ('extent-uad.yaml', resourceB), ('../common-core/link.yaml', resourceC), ('../../schemas/common-geodata/dataType.yaml', resourceD), ('extent.yaml', resourceE)])

    # Register the schema a in the registry as a resource
    # registry = Registry().with_resource(uri=f'file://{base_dir}/', resource=resource)
    registry = registry.crawl()

    validator = Draft202012Validator(schema_a, registry=registry)
    # validator.validate(instance)
    # Collect all errors
    errors = list(validator.iter_errors(instance))

    output = helper_validation_error_message(errors, url, collection_id)

    if output['error_messages'] and output['error_info']:

        TEST_SUMMARY['Test Coverage Collection Root']['Errors'] += output['error_info']

        end_time = time.time()  # Capture end time after the test has run
        elapsed_time = end_time - start_time
        COVERAGE_COLLECTION_ROOT_TIME += elapsed_time
        TEST_SUMMARY['Test Coverage Collection Root']['Elapsed Time'] = COVERAGE_COLLECTION_ROOT_TIME

        # Raise a ValidationError with all error messages
        raise ValidationError("\n\n".join(output['error_messages']))
    else:
        print("Instance is valid.")

        end_time = time.time()  # Capture end time after the test has run
        elapsed_time = end_time - start_time
        COVERAGE_COLLECTION_ROOT_TIME += elapsed_time
        TEST_SUMMARY['Test Coverage Collection Root']['Elapsed Time'] = COVERAGE_COLLECTION_ROOT_TIME



@pytest.mark.parametrize("url", CoverageCollectionSchemaUrlList)
def test_coverage_collection_schema(url):
    """
    Pytest function to validate the structure and content of GeoMet Coverage Collection schema JSON response.

    This test performs the following for each URL in `CoverageCollectionSchemaUrlList`:
    - Sends a GET request to the specified feature collection URL.
    - Asserts that the response has a 200 OK status.
    - Loads the JSON response and validates it against a set of predefined JSON Schemas
    - Uses a schema registry to resolve internal schema references.
    - Collects and reports validation errors with detailed messages and context.
    - Updates a global `TEST_SUMMARY` object with error details and elapsed test time.

    Parameters:
    url (str): The feature collection metadata URL to validate.

    Raises:
    AssertionError: If the HTTP response status code is not 200.
    ValidationError: If the JSON does not conform to the expected schema(s).
    """
    # test with url: https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections/climate:dcs:projected:annual:P20Y-Avg/schema?f=json

    global COVERAGE_COLLECTION_SCHEMA_TIME
    global TEST_SUMMARY
    collection_id = url.split('/collections/')[1].split('?')[0]

    start_time = time.time()  # Capture start time

    response = requests.get(url, verify="/etc/ssl/certs")

    instance = response.json()

    try:
        assert response.status_code == 200
    except AssertionError:
        error_info = {
                'collectionId': collection_id,
                'url': url,
                'errorType': 'Status Code Error',
                'statusCode': response.status_code
        }

        TEST_SUMMARY['Test Coverage Collection Schema']['Errors'].append(error_info)

        end_time = time.time()  # Capture end time after the test has run
        elapsed_time = end_time - start_time
        COVERAGE_COLLECTION_SCHEMA_TIME += elapsed_time
        TEST_SUMMARY['Test Coverage Collection Schema']['Elapsed Time'] = COVERAGE_COLLECTION_SCHEMA_TIME

        raise

    # Define the base directory
    base_dir = os.path.abspath('tests/test-files/schemasCov')


    # Load the collection.yaml file
    schema_a_path = os.path.join(base_dir, 'tms/propertiesSchema.yaml')
    with open(schema_a_path, 'r') as f:
        schema_a = yaml.safe_load(f)

    # resource for schema a
    resourceA = Resource(contents=schema_a, specification=jsonschema.DRAFT202012)

    registry = Registry().with_resources([(f'{base_dir}', resourceA)])

    registry = registry.crawl()


    validator = Draft202012Validator(schema_a, registry=registry)

    # Collect all errors
    errors = list(validator.iter_errors(instance))

    output = helper_validation_error_message(errors, url, collection_id)

    if output['error_messages'] and output['error_info']:

        TEST_SUMMARY['Test Coverage Collection Schema']['Errors'] += output['error_info']

        end_time = time.time()  # Capture end time after the test has run
        elapsed_time = end_time - start_time
        COVERAGE_COLLECTION_SCHEMA_TIME += elapsed_time
        TEST_SUMMARY['Test Coverage Collection Schema']['Elapsed Time'] = COVERAGE_COLLECTION_SCHEMA_TIME

        # Raise a ValidationError with all error messages
        raise ValidationError("\n\n".join(output['error_messages']))
    else:
        print("Instance is valid.")

        end_time = time.time()  # Capture end time after the test has run
        elapsed_time = end_time - start_time
        COVERAGE_COLLECTION_SCHEMA_TIME += elapsed_time
        TEST_SUMMARY['Test Coverage Collection Schema']['Elapsed Time'] = COVERAGE_COLLECTION_SCHEMA_TIME


# @pytest.mark.parametrize("url", coverageCollectionCoverageDataUrlList)
@pytest.mark.parametrize("url", ['https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections/weather:rdpa:10km:6p/coverage?f=json'])
def test_coverage_collection_coverageResponse(url):
    """
    Pytest function to validate the structure and content of GeoMet Coverage Collection coverage data JSON response.

    This test performs the following for each URL in `coverageCollectionCoverageDataUrlList`:
    - Sends a GET request to the specified feature collection URL.
    - Asserts that the response has a 200 OK status.
    - Loads the JSON response and validates it against a set of predefined JSON Schemas
    - Uses a schema registry to resolve internal schema references.
    - Collects and reports validation errors with detailed messages and context.
    - Updates a global `TEST_SUMMARY` object with error details and elapsed test time.

    Parameters:
    url (str): The feature collection metadata URL to validate.

    Raises:
    AssertionError: If the HTTP response status code is not 200.
    ValidationError: If the JSON does not conform to the expected schema(s).
    """
    # test with url: https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections/weather:rdpa:10km:6p/coverage?f=json

    global COVERAGE_COLLECTION_COV_RESPONSE_TIME
    global TEST_SUMMARY
    collection_id = url.split('/collections/')[1].split('?')[0]

    start_time = time.time()  # Capture start time

    response = requests.get(url, verify="/etc/ssl/certs")

    try:
        assert response.status_code == 200
    except AssertionError:
        error_info = {
                'collectionId': collection_id,
                'url': url,
                'errorType': 'Status Code Error',
                'statusCode': response.status_code
        }

        TEST_SUMMARY['Test Coverage Collection Coverage Response']['Errors'].append(error_info)

        end_time = time.time()  # Capture end time after the test has run
        elapsed_time = end_time - start_time
        COVERAGE_COLLECTION_COV_RESPONSE_TIME += elapsed_time
        TEST_SUMMARY['Test Coverage Collection Coverage Response']['Elapsed Time'] = COVERAGE_COLLECTION_COV_RESPONSE_TIME

        raise

    instance = response.json()
    # Define the base directory
    base_dir = os.path.abspath('tests/test-files/schemasCov')

    # Load the collection.yaml file
    schema_a_path = os.path.join(base_dir, 'coverage.json')
    with open(schema_a_path, 'r') as f:
        schema_a = json.load(f)

    # resource for schema a
    resourceA = Resource(contents=schema_a, specification=jsonschema.DRAFT202012)


    registry = Registry().with_resources([(f'{base_dir}', resourceA)])

    # Register the schema a in the registry as a resource
    registry = registry.crawl()

    validator = Draft202012Validator(schema_a, registry=registry)

    # validator.validate(instance)

    # Collect all errors
    errors = list(validator.iter_errors(instance))

    output = helper_validation_error_message(errors, url, collection_id)

    if output['error_messages'] and output['error_info']:

        TEST_SUMMARY['Test Coverage Collection Coverage Response']['Errors'] += output['error_info']

        end_time = time.time()  # Capture end time after the test has run
        elapsed_time = end_time - start_time
        COVERAGE_COLLECTION_COV_RESPONSE_TIME += elapsed_time
        TEST_SUMMARY['Test Coverage Collection Coverage Response']['Elapsed Time'] = COVERAGE_COLLECTION_COV_RESPONSE_TIME

        # Raise a ValidationError with all error messages
        raise ValidationError("\n\n".join(output['error_messages']))
    else:
        print("Instance is valid.")

        end_time = time.time()  # Capture end time after the test has run
        elapsed_time = end_time - start_time
        COVERAGE_COLLECTION_COV_RESPONSE_TIME += elapsed_time
        TEST_SUMMARY['Test Coverage Collection Coverage Response']['Elapsed Time'] = COVERAGE_COLLECTION_COV_RESPONSE_TIME


# @pytest.mark.parametrize("url", CoverageCollectionSchemaUrlList)
@pytest.mark.parametrize("url", ['https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections/weather:rdpa:10km:6p/schema?f=json'])
def test_coverage_collection_eachVariableProperty(url):
    """
    Pytest function to validate the structure and content of GeoMet Coverage Collection coverage property data JSON response.

    This test performs the following for each URL in `CoverageCollectionSchemaUrlList`:
    - Sends a GET request to the specified feature collection URL.
    - Asserts that the response has a 200 OK status.
    - Loads the JSON response and validates it against a set of predefined JSON Schemas
    - Uses a schema registry to resolve internal schema references.
    - Collects and reports validation errors with detailed messages and context.
    - Updates a global `TEST_SUMMARY` object with error details and elapsed test time.

    Parameters:
    url (str): The feature collection metadata URL to validate.

    Raises:
    AssertionError: If the HTTP response status code is not 200.
    ValidationError: If the JSON does not conform to the expected schema(s).
    """
    # test with url: https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections/weather:rdpa:10km:6p/schema?f=json

    global COVERAGE_COLLECTION_VARIABLE_PROPERTY_TIME
    global TEST_SUMMARY

    error_message_list = []
    error_info_list = []


    collection_id = url.split('/collections/')[1].split('?')[0]

    start_time = time.time()  # Capture start time

    response = requests.get(url, verify="/etc/ssl/certs")

    instance = response.json()

    # assert response.status_code == 200
    try:
        assert response.status_code == 200
    except AssertionError:
        error_info = {
                'collectionId': collection_id,
                'url': url,
                'errorType': 'Status Code Error',
                'statusCode': response.status_code
        }

        TEST_SUMMARY['Test Coverage Collection Variable Property']['Errors'].append(error_info)

        end_time = time.time()  # Capture end time after the test has run
        elapsed_time = end_time - start_time
        COVERAGE_COLLECTION_VARIABLE_PROPERTY_TIME += elapsed_time
        TEST_SUMMARY['Test Coverage Collection Variable Property']['Elapsed Time'] = COVERAGE_COLLECTION_VARIABLE_PROPERTY_TIME

        raise

    for property in instance['properties']:
        newUrl = url.replace('/schema?f=json', f'/coverage?f=json&properties={property}')

        output = helper_coverage_response_validation(newUrl)

        error_info_list += output['error_info']
        error_message_list += output['error_messages']

    if error_info_list and error_message_list:

        TEST_SUMMARY['Test Coverage Collection Variable Property']['Errors'] += error_info_list

        end_time = time.time()  # Capture end time after the test has run
        elapsed_time = end_time - start_time
        COVERAGE_COLLECTION_VARIABLE_PROPERTY_TIME += elapsed_time
        TEST_SUMMARY['Test Coverage Collection Variable Property']['Elapsed Time'] = COVERAGE_COLLECTION_VARIABLE_PROPERTY_TIME


        print('here you go', error_message_list)

        # Raise a ValidationError with all error messages
        raise ValidationError("\n\n".join(error_message_list))

    else:
        end_time = time.time()  # Capture end time after the test has run
        elapsed_time = end_time - start_time
        COVERAGE_COLLECTION_VARIABLE_PROPERTY_TIME += elapsed_time
        TEST_SUMMARY['Test Coverage Collection Variable Property']['Elapsed Time'] = COVERAGE_COLLECTION_VARIABLE_PROPERTY_TIME

# @pytest.mark.parametrize("url", CoverageCollectionRootUrlList)
@pytest.mark.parametrize("url", ['https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections/weather:rdpa:10km:6p?f=json'])
def test_coverage_collection_extents(url):
    """
    Pytest function to validate the structure and content of GeoMet Coverage Collection coverage extent data JSON response.

    This test performs the following for each URL in `CoverageCollectionSchemaUrlList`:
    - Sends a GET request to the specified feature collection URL.
    - Asserts that the response has a 200 OK status.
    - Loads the JSON response and validates it against a set of predefined JSON Schemas
    - Uses a schema registry to resolve internal schema references.
    - Collects and reports validation errors with detailed messages and context.
    - Updates a global `TEST_SUMMARY` object with error details and elapsed test time.

    Parameters:
    url (str): The feature collection metadata URL to validate.

    Raises:
    AssertionError: If the HTTP response status code is not 200.
    ValidationError: If the JSON does not conform to the expected schema(s).
    """

    # test with url: https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections/weather:rdpa:10km:6p?f=json

    global COVERAGE_COLLECTION_EXTENTS_TIME
    global TEST_SUMMARY

    error_message_list = []
    error_info_list = []

    collection_id = url.split('/collections/')[1].split('?')[0]

    start_time = time.time()  # Capture start time

    response = requests.get(url, verify="/etc/ssl/certs")

    # assert response.status_code == 200
    try:
        assert response.status_code == 200
    except AssertionError:
        error_info = {
                'collectionId': collection_id,
                'url': url,
                'errorType': 'Status Code Error',
                'statusCode': response.status_code
        }

        TEST_SUMMARY['Test Coverage Collection Extents']['Errors'].append(error_info)

        end_time = time.time()  # Capture end time after the test has run
        elapsed_time = end_time - start_time
        COVERAGE_COLLECTION_EXTENTS_TIME += elapsed_time
        TEST_SUMMARY['Test Coverage Collection Extents']['Elapsed Time'] = COVERAGE_COLLECTION_EXTENTS_TIME

        raise

    instance = response.json()

    for i in instance['extent']:

        if i == 'spatial':
            bbox = instance['extent']['spatial']['bbox'][0]
            bboxString = ",".join(map(str, bbox))
            newUrl = url.replace(f'{instance["id"]}?f=json', f'{instance["id"]}/coverage?f=json&bbox={bboxString}')

        elif i == 'period':
            period = instance['extent']['period']['interval'][0]
            newUrl = url.replace(f'{instance["id"]}?f=json', f'{instance["id"]}/coverage?f=json&subset=period("{period}")')

        elif i == 'reference_time':
            reference_time = instance['extent']['reference_time']['interval'][0][0]
            newUrl = url.replace(f'{instance["id"]}?f=json', f'{instance["id"]}/coverage?f=json&subset=reference_time("{reference_time}")')

        elif i == 'temporal':
            temporal = instance['extent']['temporal']['interval'][0]
            newUrl = url.replace(f'{instance["id"]}?f=json', f'{instance["id"]}/coverage?f=json&datetime={temporal[0]}')

        elif i == 'percentile':
            percentile = instance['extent']['percentile']['interval'][0][0]
            newUrl = url.replace(f'{instance["id"]}?f=json', f'{instance["id"]}/coverage?f=json&subset=percentile("{percentile}")')

        elif i == 'scenario':
            scenario = instance['extent']['scenario']['interval'][0][0]
            newUrl = url.replace(f'{instance["id"]}?f=json', f'{instance["id"]}/coverage?f=json&subset=scenario("{scenario}")')

        elif i == 'season':
            season = instance['extent']['season']['interval'][0][0]
            newUrl = url.replace(f'{instance["id"]}?f=json', f'{instance["id"]}/coverage?f=json&subset=season("{season}")')

        elif re.match(r"^P\d+Y-Avg$", i):
            P20YAvg = instance['extent'][i]['interval'][0][0]
            newUrl = url.replace(f'{instance["id"]}?f=json', f'{instance["id"]}/coverage?f=json&subset={i}("{P20YAvg}")')

        output = helper_coverage_response_validation(newUrl)

        error_info_list += output['error_info']
        error_message_list += output['error_messages']

    if error_info_list and error_message_list:

        TEST_SUMMARY['Test Coverage Collection Extents']['Errors'] += error_info_list

        end_time = time.time()  # Capture end time after the test has run
        elapsed_time = end_time - start_time
        COVERAGE_COLLECTION_EXTENTS_TIME += elapsed_time
        TEST_SUMMARY['Test Coverage Collection Extents']['Elapsed Time'] = COVERAGE_COLLECTION_EXTENTS_TIME


        # Raise a ValidationError with all error messages
        raise ValidationError("\n\n".join(error_message_list))

    else:
        end_time = time.time()  # Capture end time after the test has run
        elapsed_time = end_time - start_time
        COVERAGE_COLLECTION_EXTENTS_TIME += elapsed_time
        TEST_SUMMARY['Test Coverage Collection Extents']['Elapsed Time'] = COVERAGE_COLLECTION_EXTENTS_TIME


@pytest.mark.parametrize("url", processUrlList)
def test_process_collection(url):
    """
    Pytest function to validate the structure and content of GeoMet Process Collection root JSON response.

    This test performs the following for each URL in `processUrlList`:
    - Sends a GET request to the specified feature collection URL.
    - Asserts that the response has a 200 OK status.
    - Loads the JSON response and validates it against a set of predefined JSON Schemas
    - Uses a schema registry to resolve internal schema references.
    - Collects and reports validation errors with detailed messages and context.
    - Updates a global `TEST_SUMMARY` object with error details and elapsed test time.

    Parameters:
    url (str): The feature collection metadata URL to validate.

    Raises:
    AssertionError: If the HTTP response status code is not 200.
    ValidationError: If the JSON does not conform to the expected schema(s).
    """

    # test with url: https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/processes/raster-drill?f=json
    global PROCESS_COLLECTION_ROOT_TIME
    global TEST_SUMMARY
    collection_id = url.split('/processes/')[1].split('?')[0]

    start_time = time.time()  # Capture start time

    response = requests.get(url, verify="/etc/ssl/certs")

    instance = response.json()

    # assert response.status_code == 200
    try:
        assert response.status_code == 200
    except AssertionError:
        error_info = {
                'collectionId': collection_id,
                'url': url,
                'errorType': 'Status Code Error',
                'statusCode': response.status_code
        }

        TEST_SUMMARY['Test Process Collection Root']['Errors'].append(error_info)

        end_time = time.time()  # Capture end time after the test has run
        elapsed_time = end_time - start_time
        PROCESS_COLLECTION_ROOT_TIME += elapsed_time
        TEST_SUMMARY['Test Process Collection Root']['Elapsed Time'] = PROCESS_COLLECTION_ROOT_TIME

        raise

    # Define the base directory
    base_dir = os.path.abspath('tests/test-files/schemasProc')

    # Load the landingPage.yaml file
    schema_a_path = os.path.join(base_dir, 'landingPage.yaml')
    with open(schema_a_path, 'r') as f:
        schema_a = yaml.safe_load(f)

    schema_b_path = os.path.join(base_dir, 'link.yaml')
    with open(schema_b_path, 'r') as f:
        schema_b = yaml.safe_load(f)

    # resource for schema a
    resourceA = Resource(contents=schema_a, specification=jsonschema.DRAFT202012)

    # resource for schema b
    resourceB = Resource(contents=schema_b, specification=jsonschema.DRAFT202012)

    registry = Registry().with_resources([('landingPage.yaml', resourceA), ('link.yaml', resourceB)])

    # Register the schema a in the registry as a resource
    registry = registry.crawl()

    validator = Draft202012Validator(schema_a, registry=registry)

    errors = list(validator.iter_errors(instance))

    output = helper_validation_error_message(errors, url, collection_id)

    if output['error_messages'] and output['error_info']:

        TEST_SUMMARY['Test Process Collection Root']['Errors'] += output['error_info']

        end_time = time.time()  # Capture end time after the test has run
        elapsed_time = end_time - start_time
        PROCESS_COLLECTION_ROOT_TIME += elapsed_time
        TEST_SUMMARY['Test Process Collection Root']['Elapsed Time'] = PROCESS_COLLECTION_ROOT_TIME

        # Raise a ValidationError with all error messages
        raise ValidationError("\n\n".join(output['error_messages']))
    else:
        print("Instance is valid.")

    end_time = time.time()  # Capture end time after the test has run
    elapsed_time = end_time - start_time
    PROCESS_COLLECTION_ROOT_TIME += elapsed_time
    TEST_SUMMARY['Test Process Collection Root']['Elapsed Time'] = PROCESS_COLLECTION_ROOT_TIME

@pytest.mark.parametrize("url", processExecutionUrlList)
def test_process_collection_execute(url):
    """
    Pytest function to validate the structure and content of GeoMet Process Collection execute response.

    This test performs the following for each URL in `processExecutionUrlList`:
    - Sends a POST request to the specified feature collection URL.
    - Asserts that the response has a 200 OK status.
    - Loads the JSON response and validates it against a predefined Schema
    - Uses a schema registry to resolve internal schema references.
    - Collects and reports validation errors with detailed messages and context.
    - Updates a global `TEST_SUMMARY` object with error details and elapsed test time.

    Parameters:
    url (str): The feature collection metadata URL to validate.

    Raises:
    AssertionError: If the HTTP response status code is not 200.
    ValidationError: If the JSON does not conform to the expected schema(s).
    """
    # test with url: https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/processes/raster-drill/execution

    global PROCESS_COLLECTION_EXECUTE_TIME
    global TEST_SUMMARY
    print(url)
    collection_id = url.split('/')[5]
    print(url.split('/'))
    start_time = time.time()  # Capture start time

    # Data to send with the request (typically a dictionary)
    data = {
          "inputs": {
            "format": "CSV",
            "layer": "CMIP5.TT.RCP26.YEAR.ANO_PCTL50",
            "x": -114.74968888274337,
            "y": 51.132831196692806
            }
    }

    # Sending a POST request with the data
    response = requests.post(url, json=data, verify="/etc/ssl/certs")

    # Checking the response status code
    try:
        assert response.status_code == 200
    except AssertionError:
        error_info = {
                'collectionId': collection_id,
                'url': url,
                'errorType': 'Status Code Error',
                'statusCode': response.status_code
        }

        TEST_SUMMARY['Test Process Collection Execute']['Errors'].append(error_info)

        end_time = time.time()  # Capture end time after the test has run
        elapsed_time = end_time - start_time
        PROCESS_COLLECTION_EXECUTE_TIME += elapsed_time
        TEST_SUMMARY['Test Process Collection Execute']['Elapsed Time'] = PROCESS_COLLECTION_EXECUTE_TIME

        raise

    response_text = response.text.replace('\r\n', '\n')

    if collection_id == 'raster-drill':
        with open('tests/test-files/schemasProc/rasterDrillExecution.txt', 'r') as f:
            file_content = f.read()

    # Read the contents of the file into a string
    try:
        assert file_content == response_text
    except AssertionError:
        end_time = time.time()  # Capture end time after the test has run
        elapsed_time = end_time - start_time
        PROCESS_COLLECTION_EXECUTE_TIME += elapsed_time
        TEST_SUMMARY['Test Process Collection Execute']['Elapsed Time'] = PROCESS_COLLECTION_EXECUTE_TIME
        TEST_SUMMARY['Test Process Collection Execute']['Errors'] = 'Assertion Error'
        raise

    end_time = time.time()  # Capture end time after the test has run
    elapsed_time = end_time - start_time
    PROCESS_COLLECTION_EXECUTE_TIME += elapsed_time
    TEST_SUMMARY['Test Process Collection Execute']['Elapsed Time'] = PROCESS_COLLECTION_EXECUTE_TIME
