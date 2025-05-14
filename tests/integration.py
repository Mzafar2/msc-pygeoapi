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
# from referencing.exceptions import ReferenceResolutionError
import json
import os

# @pytest.fixture()
# def url(pytestconfig):
#     return pytestconfig.getoption('url')


# add variables for creating the json test summary

COVERAGE_COLLECTION_ROOT_TIME = 0
COVERAGE_COLLECTION_SCHEMA_TIME = 0
COVERAGE_COLLECTION_COV_RESPONSE_TIME = 0
FEATURE_COLLECTION_SINGLE_ITEM_TIME = 0
FEATURE_COLLECTION_ITEMS_TIME = 0
FEATURE_COLLECTION_ROOT_TIME = 0
COVERAGE_COLLECTION_VARIABLE_PROPERTY_TIME = 0
PROCESS_COLLECTION_ROOT_TIME = 0
PROCESS_COLLECTION_EXECUTE_TIME = 0

TEST_SUMMARY = {
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


    # print(f"Here is the total test timeeee sirr {COVERAGE_COLLECTION_ROOT_TIME}")
    # print(TEST_SUMMARY)
    print(json.dumps(TEST_SUMMARY, indent=4))


    # Write it to a JSON file
    with open("tests/test-files/test_summary.json", "w") as f:
        json.dump(TEST_SUMMARY, f, indent=4)

# def preprocess_none_to_null(data):
#     """
#     Recursively process a dictionary or list and replace Python's None values with 'null' (as a string).
#     """
#     if isinstance(data, dict):  # Check if it's a dictionary
#         return {key: preprocess_none_to_null(value) for key, value in data.items()}
#     elif isinstance(data, list):  # If it's a list
#         return [preprocess_none_to_null(item) for item in data]
#     elif data is None:  # If the value is None, replace it with 'null'
#         return 'null'
#     else:
#         return data  # Return the value as-is if it's not None, list, or dict

# def error_bypass(instance, validator):
#     # Perform validation and collect all errors
#     validation_errors = []
#     for e in validator.iter_errors(instance):
#         validation_errors.append(str(e))

#     if validation_errors:
#         # Print all errors
#         print("Validation Errors:")
#         for error in validation_errors:
#             print(error)
#     else:
#         print("No validation errors found.")


#  Setup helper functions below

def helper_coverage_response_validation(url):

    print(f'here is the url ok: {url}')

    output = {'error_messages': None, 'error_info': None}

    collection_id = url.split('/collections/')[1].split('?')[0]

    response = requests.get(url, verify="/etc/ssl/certs")

    # instance = response.json()


    try:
        assert response.status_code == 200
    except AssertionError:
        error_info = {
                'collectionId': collection_id,
                'url': url,
                'errorType': 'Status Code Error',
                'statusCode': response.status_code
        }

        output['error_info'] = error_info

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

            output['error_messages'] = error_messages
            # Fill test summary dict

            error_info = {
                'collectionId': collection_id,
                'url': url,
                'errorType': 'Validation Error',
                'failedSchemaItem': schema_path,
                'failedInstanceItem': instance_path,
                'errorMessage': error.message
            }

            output['error_info'] = error_info

    return output


def get_feature_collection_root_urls():
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
    url = 'https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/processes?f=json'
    urlList = []
    response = requests.get(url, verify="/etc/ssl/certs")

    instance = response.json()

    assert response.status_code == 200

    for process in instance['processes']:
        urlToAdd = f"https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/processes/{process['id']}/execution?f=json"
        urlList.append(urlToAdd)

    return urlList


# Setup url variables for making arguments during the testing below

featureCollectionRootUrlList = get_feature_collection_root_urls()
featureCollectionItemsUrlList = get_feature_collection_items_urls()
featureCollectionSingleItemsUrlList = get_feature_collection_single_items_urls()
CoverageCollectionRootUrlList = get_coverage_collection_root_urls()
CoverageCollectionSchemaUrlList = get_coverage_collection_schema_urls()
coverageCollectionCoverageDataUrlList = get_coverage_collection_coverageData_urls()
processUrlList = get_process_urls()
processExecutionUrlList = get_process_execution_urls()





# tests
@pytest.mark.parametrize("url", featureCollectionRootUrlList)
def est_feature_collection_root(url):

    # test with url: https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections/climate-normals?f=json
    url = 'https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections/climate-normals?f=json'
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

            # Fill test summary dict

            error_info = {
                'collectionId': collection_id,
                'url': url,
                'errorType': 'Validation Error',
                'failedSchemaItem': schema_path,
                'failedInstanceItem': instance_path,
                'errorMessage': error.message
            }

            TEST_SUMMARY['Test Feature Collection Root']['Errors'].append(error_info)

        end_time = time.time()  # Capture end time after the test has run
        elapsed_time = end_time - start_time
        FEATURE_COLLECTION_ROOT_TIME += elapsed_time
        TEST_SUMMARY['Test Feature Collection Root']['Elapsed Time'] = FEATURE_COLLECTION_ROOT_TIME

        # Raise a ValidationError with all error messages
        raise ValidationError("\n\n".join(error_messages))
    else:
        print("Instance is valid.")

    end_time = time.time()  # Capture end time after the test has run
    elapsed_time = end_time - start_time
    FEATURE_COLLECTION_ROOT_TIME += elapsed_time
    TEST_SUMMARY['Test Feature Collection Root']['Elapsed Time'] = FEATURE_COLLECTION_ROOT_TIME

@pytest.mark.parametrize("url", featureCollectionItemsUrlList)
def est_feature_collection_items(url):

    # test with url: https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections/climate-normals/items?limit=1&f=json
    # url = 'https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections/hurricanes-wind_radii-realtime/items?limit=1&f=json'
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

            # Fill test summary dict

            error_info = {
                'collectionId': collection_id,
                'url': url,
                'errorType': 'Validation Error',
                'failedSchemaItem': schema_path,
                'failedInstanceItem': instance_path,
                'errorMessage': error.message
            }

            TEST_SUMMARY['Test Feature Collection Items']['Errors'].append(error_info)

        end_time = time.time()  # Capture end time after the test has run
        elapsed_time = end_time - start_time
        FEATURE_COLLECTION_ITEMS_TIME += elapsed_time
        TEST_SUMMARY['Test Feature Collection Items']['Elapsed Time'] = FEATURE_COLLECTION_ITEMS_TIME

        # Raise a ValidationError with all error messages
        raise ValidationError("\n\n".join(error_messages))
    else:
        print("Instance is valid.")

    end_time = time.time()  # Capture end time after the test has run
    elapsed_time = end_time - start_time
    FEATURE_COLLECTION_ITEMS_TIME += elapsed_time
    TEST_SUMMARY['Test Feature Collection Items']['Elapsed Time'] = FEATURE_COLLECTION_ITEMS_TIME


@pytest.mark.parametrize("url", featureCollectionSingleItemsUrlList)
def est_feature_collection_single_item(url):

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

            # Fill test summary dict

            error_info = {
                'collectionId': collection_id,
                'url': url,
                'errorType': 'Validation Error',
                'failedSchemaItem': schema_path,
                'failedInstanceItem': instance_path,
                'errorMessage': error.message
            }

            TEST_SUMMARY['Test Feature Collection Single Item']['Errors'].append(error_info)

        end_time = time.time()  # Capture end time after the test has run
        elapsed_time = end_time - start_time
        FEATURE_COLLECTION_SINGLE_ITEM_TIME += elapsed_time
        TEST_SUMMARY['Test Feature Collection Single Item']['Elapsed Time'] = FEATURE_COLLECTION_SINGLE_ITEM_TIME

        # Raise a ValidationError with all error messages
        raise ValidationError("\n\n".join(error_messages))
    else:
        print("Instance is valid.")

    end_time = time.time()  # Capture end time after the test has run
    elapsed_time = end_time - start_time
    FEATURE_COLLECTION_SINGLE_ITEM_TIME += elapsed_time
    TEST_SUMMARY['Test Feature Collection Single Item']['Elapsed Time'] = FEATURE_COLLECTION_SINGLE_ITEM_TIME


@pytest.mark.parametrize("url", CoverageCollectionRootUrlList)
def est_coverage_collection_root(url):
    # test with url: https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections/climate:dcs:projected:annual:P20Y-Avg?f=json
    # url = 'https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections/climate:cangrd:historical:seasonal:anomaly'
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

            # Fill test summary dict

            error_info = {
                'collectionId': collection_id,
                'url': url,
                'errorType': 'Validation Error',
                'failedSchemaItem': schema_path,
                'failedInstanceItem': instance_path,
                'errorMessage': error.message
            }

            TEST_SUMMARY['Test Coverage Collection Root']['Errors'].append(error_info)

            end_time = time.time()  # Capture end time after the test has run
            elapsed_time = end_time - start_time
            COVERAGE_COLLECTION_ROOT_TIME += elapsed_time
            TEST_SUMMARY['Test Coverage Collection Root']['Elapsed Time'] = COVERAGE_COLLECTION_ROOT_TIME

        # Raise a ValidationError with all error messages
        raise ValidationError("\n\n".join(error_messages))
    else:
        print("Instance is valid.")

    end_time = time.time()  # Capture end time after the test has run
    elapsed_time = end_time - start_time
    COVERAGE_COLLECTION_ROOT_TIME += elapsed_time
    TEST_SUMMARY['Test Coverage Collection Root']['Elapsed Time'] = COVERAGE_COLLECTION_ROOT_TIME



@pytest.mark.parametrize("url", CoverageCollectionSchemaUrlList)
def est_coverage_collection_schema(url):
    # test with url: https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections/climate:dcs:projected:annual:P20Y-Avg/schema?f=json

    # url = 'https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections/climate:spei-12:projected/schema?f=json'

    global COVERAGE_COLLECTION_SCHEMA_TIME
    global TEST_SUMMARY
    collection_id = url.split('/collections/')[1].split('?')[0]

    start_time = time.time()  # Capture start time

    response = requests.get(url, verify="/etc/ssl/certs")

    instance = response.json()

    # assert response.status_code == 200
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

    # Register the schema a in the registry as a resource
    # registry = Registry().with_resource(uri=f'file://{base_dir}/', resource=resource)
    registry = registry.crawl()

    # instance = preprocess_none_to_null(instance)


    validator = Draft202012Validator(schema_a, registry=registry)
    # validator.validate(instance)

    # Collect all errors
    errors = list(validator.iter_errors(instance))

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

            # Fill test summary dict

            error_info = {
                'collectionId': collection_id,
                'url': url,
                'errorType': 'Validation Error',
                'failedSchemaItem': schema_path,
                'failedInstanceItem': instance_path,
                'errorMessage': error.message
            }

            TEST_SUMMARY['Test Coverage Collection Schema']['Errors'].append(error_info)


        end_time = time.time()  # Capture end time after the test has run
        elapsed_time = end_time - start_time
        COVERAGE_COLLECTION_SCHEMA_TIME += elapsed_time
        TEST_SUMMARY['Test Coverage Collection Schema']['Elapsed Time'] = COVERAGE_COLLECTION_SCHEMA_TIME

        # Raise a ValidationError with all error messages
        raise ValidationError("\n\n".join(error_messages))
    else:
        print("Instance is valid.")

    end_time = time.time()  # Capture end time after the test has run
    elapsed_time = end_time - start_time
    COVERAGE_COLLECTION_SCHEMA_TIME += elapsed_time
    TEST_SUMMARY['Test Coverage Collection Schema']['Elapsed Time'] = COVERAGE_COLLECTION_SCHEMA_TIME


@pytest.mark.parametrize("url", coverageCollectionCoverageDataUrlList)
def est_coverage_collection_coverageResponse(url):
    # test with url: https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections/climate:dcs:projected:annual:P20Y-Avg/coverage?f=json
    # test with url: http://geomet-dev-31.edc-mtl.ec.gc.ca:8089/collections/weather:cansips:100km:forecast:seasonal-products/coverage?f=json&bbox=-141,45,-137,47&subset=period\(%22P02M-P04M%22\),reference_time\(%222025-03%22\)
    # test with url: http://geomet-dev-31.edc-mtl.ec.gc.ca:8089/collections/weather:cansips:100km:forecast:seasonal-products/coverage?f=json&bbox=-141,45,-137,47&subset=period\(%22P02M-P04M%22\),reference_time\(%222025-03%22\)
    #  if nthis here u good 
    # url = 'https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections/climate:dcs:projected:annual:anomaly/coverage?f=json'

    global COVERAGE_COLLECTION_COV_RESPONSE_TIME
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

        TEST_SUMMARY['Test Coverage Collection Coverage Response']['Errors'].append(error_info)

        end_time = time.time()  # Capture end time after the test has run
        elapsed_time = end_time - start_time
        COVERAGE_COLLECTION_COV_RESPONSE_TIME += elapsed_time
        TEST_SUMMARY['Test Coverage Collection Coverage Response']['Elapsed Time'] = COVERAGE_COLLECTION_COV_RESPONSE_TIME

        raise

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

            # Fill test summary dict

            error_info = {
                'collectionId': collection_id,
                'url': url,
                'errorType': 'Validation Error',
                'failedSchemaItem': schema_path,
                'failedInstanceItem': instance_path,
                'errorMessage': error.message
            }

            TEST_SUMMARY['Test Coverage Collection Coverage Response']['Errors'].append(error_info)

        end_time = time.time()  # Capture end time after the test has run
        elapsed_time = end_time - start_time
        COVERAGE_COLLECTION_COV_RESPONSE_TIME += elapsed_time
        TEST_SUMMARY['Test Coverage Collection Coverage Response']['Elapsed Time'] = COVERAGE_COLLECTION_COV_RESPONSE_TIME


        # Raise a ValidationError with all error messages
        raise ValidationError("\n\n".join(error_messages))
    else:
        print("Instance is valid.")

    end_time = time.time()  # Capture end time after the test has run
    elapsed_time = end_time - start_time
    COVERAGE_COLLECTION_COV_RESPONSE_TIME += elapsed_time
    TEST_SUMMARY['Test Coverage Collection Coverage Response']['Elapsed Time'] = COVERAGE_COLLECTION_COV_RESPONSE_TIME


# @pytest.mark.parametrize("url", CoverageCollectionSchemaUrlList)
def test_coverage_collection_eachVariableProperty(url):
    # test with url: https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections/climate:dcs:projected:annual:P20Y-Avg/schema?f=json
    url = 'https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections/climate:cangrd:historical:annual:anomaly/schema?f=json'
    global COVERAGE_COLLECTION_VARIABLE_PROPERTY_TIME
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

        TEST_SUMMARY['Test Coverage Collection Variable Property']['Errors'].append(error_info)

        end_time = time.time()  # Capture end time after the test has run
        elapsed_time = end_time - start_time
        COVERAGE_COLLECTION_VARIABLE_PROPERTY_TIME += elapsed_time
        TEST_SUMMARY['Test Coverage Collection Variable Property']['Elapsed Time'] = COVERAGE_COLLECTION_VARIABLE_PROPERTY_TIME

        raise

    for property in instance['properties']:
        a=url.replace('/schema?f=json', f'/coverage?f=json&properties={property}')

        output = helper_coverage_response_validation(a)

        if output['error_info'] and output['messages']:

            TEST_SUMMARY['Test Coverage Collection Variable Property']['Errors'].append(output['error_info'])

            end_time = time.time()  # Capture end time after the test has run
            elapsed_time = end_time - start_time
            COVERAGE_COLLECTION_VARIABLE_PROPERTY_TIME += elapsed_time
            TEST_SUMMARY['Test Coverage Collection Variable Property']['Elapsed Time'] = COVERAGE_COLLECTION_VARIABLE_PROPERTY_TIME

            # Raise a ValidationError with all error messages
            raise ValidationError("\n\n".join(output['messages']))

        else:
            end_time = time.time()  # Capture end time after the test has run
            elapsed_time = end_time - start_time
            COVERAGE_COLLECTION_VARIABLE_PROPERTY_TIME += elapsed_time
            TEST_SUMMARY['Test Coverage Collection Variable Property']['Elapsed Time'] = COVERAGE_COLLECTION_VARIABLE_PROPERTY_TIME

        # est_coverage_collection_coverageResponse(a)

# WAIT UNTIL NEW EXTENTS COME FOR COVERAGE COLLECTIONS
# @pytest.mark.parametrize("url", CoverageCollectionRootUrlList)
def est_coverage_collection_extents(url):
    # test with url: https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections/climate:dcs:projected:annual:P20Y-Avg?f=json
    url = 'https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections/climate:dcs:projected:annual:P20Y-Avg?f=json'
    global COVERAGE_COLLECTION_EXTENTS_TIME
    global TEST_SUMMARY
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

        TEST_SUMMARY['Coverage Collection Extents Test']['Errors'].append(error_info)

        end_time = time.time()  # Capture end time after the test has run
        elapsed_time = end_time - start_time
        COVERAGE_COLLECTION_EXTENTS_TIME += elapsed_time
        TEST_SUMMARY['Coverage Collection Extents Test']['Elapsed Time'] = COVERAGE_COLLECTION_EXTENTS_TIME

        raise

    instance = response.json()

    print(instance['id'])
    for i in instance['extent']:
        print(i)

        if i == 'spatial':
            bbox = instance['extent']['spatial']['bbox'][0]
            bboxString = ",".join(map(str, bbox))
            newUrl = url.replace(f'{instance["id"]}?f=json', f'{instance["id"]}/coverage?f=json&bbox={bboxString}')
            # print(newUrl)
        
        elif i == 'period':
            period = instance['extent']['period']['interval'][0]
            # print(period)
            newUrl = url.replace(f'{instance["id"]}?f=json', f'{instance["id"]}/coverage?f=json&subset=period("{period}")')
            # print(newUrl)

        elif i == 'reference_time':
            reference_time = instance['extent']['reference_time']['interval'][0][0]
            # print(reference_time)
            newUrl = url.replace(f'{instance["id"]}?f=json', f'{instance["id"]}/coverage?f=json&subset=reference_time("{reference_time}")')
            # print(newUrl)

        elif i == 'temporal':
            temporal = instance['extent']['temporal']['interval'][0]
            # print(temporal)
            newUrl = url.replace(f'{instance["id"]}?f=json', f'{instance["id"]}/coverage?f=json&datetime={temporal[0]}/{temporal[1]}')
            print(newUrl)

        elif i == 'percentile':
            percentile = instance['extent']['percentile']['interval'][0][0]
            # print(reference_time)
            newUrl = url.replace(f'{instance["id"]}?f=json', f'{instance["id"]}/coverage?f=json&subset=percentile("{percentile}")')
            print(newUrl)

        elif i == 'scenario':
            scenario = instance['extent']['scenario']['interval'][0][0]
            # print(scenario)
            newUrl = url.replace(f'{instance["id"]}?f=json', f'{instance["id"]}/coverage?f=json&subset=scenario("{scenario}")')
            print(newUrl)

        elif i == 'season':
            season = instance['extent']['season']['interval'][0][0]
            # print(season)
            newUrl = url.replace(f'{instance["id"]}?f=json', f'{instance["id"]}/coverage?f=json&subset=season("{season}")')
            print(newUrl)

        elif re.match(r"^P\d+Y-Avg$", i):
            P20YAvg = instance['extent'][i]['interval'][0][0]
            # print(season)
            newUrl = url.replace(f'{instance["id"]}?f=json', f'{instance["id"]}/coverage?f=json&subset={i}("{P20YAvg}")')
            print(newUrl)
            print("Matched pattern")


        output = helper_coverage_response_validation(newUrl)

        if output['error_info'] and output['messages']:

            TEST_SUMMARY['Coverage Collection Extents Test']['Errors'].append(output['error_info'])

            end_time = time.time()  # Capture end time after the test has run
            elapsed_time = end_time - start_time
            COVERAGE_COLLECTION_EXTENTS_TIME += elapsed_time
            TEST_SUMMARY['Coverage Collection Extents Test']['Elapsed Time'] = COVERAGE_COLLECTION_EXTENTS_TIME

            # Raise a ValidationError with all error messages
            raise ValidationError("\n\n".join(output['messages']))

        else:
            end_time = time.time()  # Capture end time after the test has run
            elapsed_time = end_time - start_time
            COVERAGE_COLLECTION_EXTENTS_TIME += elapsed_time
            TEST_SUMMARY['Coverage Collection Extents Test']['Elapsed Time'] = COVERAGE_COLLECTION_EXTENTS_TIME
    # bbox = instance['extent']['spatial']['bbox'][0]
    # bboxString = ",".join(map(str, bbox))
    # print('over hereeeee')
    # print(instance['extent']['spatial']['bbox'][0])

    # newUrl=url.replace('?f=json', '/schema?f=json')



    # response = requests.get(newUrl, verify="/etc/ssl/certs")
    # assert response.status_code == 200
    # instance = response.json()



@pytest.mark.parametrize("url", processUrlList)
def est_process_collection(url):

    # test with url: https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/processes/raster-drill?f=json
    global PROCESS_COLLECTION_ROOT_TIME
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
    # validator.validate(instance)
    errors = list(validator.iter_errors(instance))

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

            # Fill test summary dict

            error_info = {
                'collectionId': collection_id,
                'url': url,
                'errorType': 'Validation Error',
                'failedSchemaItem': schema_path,
                'failedInstanceItem': instance_path,
                'errorMessage': error.message
            }

            TEST_SUMMARY['Test Process Collection Root']['Errors'].append(error_info)

        end_time = time.time()  # Capture end time after the test has run
        elapsed_time = end_time - start_time
        PROCESS_COLLECTION_ROOT_TIME += elapsed_time
        TEST_SUMMARY['Test Process Collection Root']['Elapsed Time'] = PROCESS_COLLECTION_ROOT_TIME

        # Raise a ValidationError with all error messages
        raise ValidationError("\n\n".join(error_messages))
    else:
        print("Instance is valid.")

    end_time = time.time()  # Capture end time after the test has run
    elapsed_time = end_time - start_time
    PROCESS_COLLECTION_ROOT_TIME += elapsed_time
    TEST_SUMMARY['Test Process Collection Root']['Elapsed Time'] = PROCESS_COLLECTION_ROOT_TIME

@pytest.mark.parametrize("url", processExecutionUrlList)
def est_process_collection_execute(url):
    # test with url: https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/processes/raster-drill/execution

    global PROCESS_COLLECTION_EXECUTE_TIME
    global TEST_SUMMARY
    collection_id = url.split('/')[5]

    start_time = time.time()  # Capture start time

    url = 'https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/processes/raster-drill/execution'

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

    # assert response.status_code == 200
    # Checking the response status code
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

        TEST_SUMMARY['Test Process Collection Execute']['Errors'].append(error_info)

        end_time = time.time()  # Capture end time after the test has run
        elapsed_time = end_time - start_time
        PROCESS_COLLECTION_EXECUTE_TIME += elapsed_time
        TEST_SUMMARY['Test Process Collection Execute']['Elapsed Time'] = PROCESS_COLLECTION_EXECUTE_TIME

        raise

    response_text = response.text.replace('\r\n', '\n')
    # print(f"Response Content:\n {response_text}")

    if collection_id == 'raster-drill':
        with open('tests/test-files/schemasProc/rasterDrillExecution.txt', 'r') as f:
            file_content = f.read()  # Read the content of the file into a string

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
