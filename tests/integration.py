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

import pytest
import requests
import yaml
import jsonschema
from jsonschema import validate
from jsonschema import Draft202012Validator
from jsonschema import exceptions
from referencing import Registry, Resource, jsonschema
# from referencing.exceptions import ReferenceResolutionError
import json
import os

@pytest.fixture()
def url(pytestconfig):
    return pytestconfig.getoption('url')


# def est_msc_pygeoapi_service_online(url):

#     # Define the base directory
#     base_dir = os.path.abspath('tests/test-files/schemasCov/common-geodata')
#     print('Base dir:', base_dir)

#     # Load the schema_a.yaml file (in dir_a)
#     schema_a_path = os.path.join(base_dir, 'collectionDesc.yaml')
#     print('Schema a path:', schema_a_path)
#     with open(schema_a_path, 'r') as f:
#         schema_a = yaml.safe_load(f)
#         print("hereeee", schema_a)

#     # Load the other schema_b.yaml file (in dir_b)
#     schema_b_path = os.path.join(base_dir, '../common-core/link.yaml')
#     print('Schema b path:', schema_b_path)
#     with open(schema_b_path, 'r') as f:
#         schema_b = yaml.safe_load(f)
#         print("hereeee", schema_b)

#     # Load the other schema_c.yaml file (in dir_c)
#     schema_c_path = os.path.join(base_dir, 'extent-uad.yaml')
#     print('Schema c path:', schema_c_path)
#     with open(schema_c_path, 'r') as f:
#         schema_c = yaml.safe_load(f)
#         print("hereeee", schema_c)

#     # Load the other schema_d.yaml file (in dir_d)
#     schema_d_path = os.path.join(base_dir, 'extent.yaml')
#     print('Schema d path:', schema_d_path)
#     with open(schema_d_path, 'r') as f:
#         schema_d = yaml.safe_load(f)
#         print("hereeee", schema_d)



#     # resource for schema a
#     resourceA = Resource(contents=schema_a, specification=jsonschema.DRAFT202012)
#     # resource for schema b
#     resourceB = Resource(contents=schema_b, specification=jsonschema.DRAFT202012)
#     # resource for schema c
#     resourceC = Resource(contents=schema_c, specification=jsonschema.DRAFT202012)
#     # resource for schema c
#     resourceD = Resource(contents=schema_d, specification=jsonschema.DRAFT202012)

#     registry = Registry().with_resources([(f'{base_dir}', resourceA), ('../common-core/link.yaml', resourceB), ('extent-uad.yaml', resourceC), ('extent.yaml', resourceD)])

#     # Register the schema a in the registry as a resource
#     # registry = Registry().with_resource(uri=f'file://{base_dir}/', resource=resource)
#     print(registry)
#     registry = registry.crawl()
#     print(registry)

#     print(registry.contents(f'{base_dir}'))


#     validator = Draft202012Validator(schema_a, registry=registry)


#     # Example instance to validate
#     # Make a basic request at the URL
#     response = requests.get(url, verify="/etc/ssl/certs")
#     instance = response.json()

#     validator.validate(instance)

#     # Perform validation, resolving any $ref in the process
#     # for error in validator.iter_errors(instance):
#     #     print(f"Validation error: {error.message}")

def est_feature_collection_root(url):

    # test with url: https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections/climate-normals?f=json

    response = requests.get(url, verify="/etc/ssl/certs")

    instance = response.json()

    assert response.status_code == 200

    # Define the base directory
    base_dir = os.path.abspath('tests/test-files/schemasFeat')
    print('Base dir:', base_dir)

    # Load the collection.yaml file
    schema_a_path = os.path.join(base_dir, 'collection.yaml')
    print('Schema a path:', schema_a_path)
    with open(schema_a_path, 'r') as f:
        schema_a = yaml.safe_load(f)
        print("hereeee", schema_a)

    # Load the other extent.yaml file
    schema_b_path = os.path.join(base_dir, 'extent.yaml')
    print('Schema b path:', schema_b_path)
    with open(schema_b_path, 'r') as f:
        schema_b = yaml.safe_load(f)
        print("hereeee", schema_b)

    # Load the other link.yaml file
    schema_c_path = os.path.join(base_dir, 'link.yaml')
    print('Schema c path:', schema_c_path)
    with open(schema_c_path, 'r') as f:
        schema_c = yaml.safe_load(f)
        print("hereeee", schema_c)

    # Load the other linkBase.yaml file
    schema_d_path = os.path.join(base_dir, 'linkBase.yaml')
    print('Schema d path:', schema_d_path)
    with open(schema_d_path, 'r') as f:
        schema_d = yaml.safe_load(f)
        print("hereeee", schema_d)

    # Load the other linkTemplate.yaml file
    schema_e_path = os.path.join(base_dir, 'linkTemplate.yaml')
    print('Schema e path:', schema_e_path)
    with open(schema_e_path, 'r') as f:
        schema_e = yaml.safe_load(f)
        print("hereeee", schema_e)


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
    print(registry)
    registry = registry.crawl()
    print(registry)

    print('here is the schema for validator', schema_a)
    validator = Draft202012Validator(schema_a, registry=registry)
    validator.validate(instance)

def est_feature_collection_items(url):

    # test with url: https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections/climate-normals/items?limit=1&f=json

    response = requests.get(url, verify="/etc/ssl/certs")

    instance = response.json()

    assert response.status_code == 200

    # Define the base directory
    base_dir = os.path.abspath('tests/test-files/schemasFeat')
    print('Base dir:', base_dir)

    # Load the featureCollectionGeoJSON.yaml file
    schema_a_path = os.path.join(base_dir, 'featureCollectionGeoJSON.yaml')
    print('Schema a path:', schema_a_path)
    with open(schema_a_path, 'r') as f:
        schema_a = yaml.safe_load(f)
        print("hereeee", schema_a)

    # Load the other featureGeoJSON.yaml file
    schema_b_path = os.path.join(base_dir, 'featureGeoJSON.yaml')
    print('Schema b path:', schema_b_path)
    with open(schema_b_path, 'r') as f:
        schema_b = yaml.safe_load(f)
        print("hereeee", schema_b)

    # Load the other link.yaml file
    schema_c_path = os.path.join(base_dir, 'link.yaml')
    print('Schema c path:', schema_c_path)
    with open(schema_c_path, 'r') as f:
        schema_c = yaml.safe_load(f)
        print("hereeee", schema_c)

    # Load the other linkBase.yaml file
    schema_d_path = os.path.join(base_dir, 'linkBase.yaml')
    print('Schema d path:', schema_d_path)
    with open(schema_d_path, 'r') as f:
        schema_d = yaml.safe_load(f)
        print("hereeee", schema_d)

    # Load the other geometryGeoJSON.yaml file
    schema_e_path = os.path.join(base_dir, 'geometryGeoJSON.yaml')
    print('Schema e path:', schema_e_path)
    with open(schema_e_path, 'r') as f:
        schema_e = yaml.safe_load(f)
        print("hereeee", schema_e)

        # Load the other pointGeoJSON.yaml file
    schema_f_path = os.path.join(base_dir, 'pointGeoJSON.yaml')
    print('Schema f path:', schema_f_path)
    with open(schema_f_path, 'r') as f:
        schema_f = yaml.safe_load(f)
        print("hereeee", schema_f)

        # Load the other multipointGeoJSON.yaml file
    schema_g_path = os.path.join(base_dir, 'multipointGeoJSON.yaml')
    print('Schema g path:', schema_g_path)
    with open(schema_g_path, 'r') as f:
        schema_g = yaml.safe_load(f)
        print("hereeee", schema_g)

        # Load the other linestringGeoJSON.yaml file
    schema_h_path = os.path.join(base_dir, 'linestringGeoJSON.yaml')
    print('Schema h path:', schema_h_path)
    with open(schema_h_path, 'r') as f:
        schema_h = yaml.safe_load(f)
        print("hereeee", schema_h)

        # Load the other multilinestringGeoJSON.yaml file
    schema_i_path = os.path.join(base_dir, 'multilinestringGeoJSON.yaml')
    print('Schema i path:', schema_i_path)
    with open(schema_i_path, 'r') as f:
        schema_i = yaml.safe_load(f)
        print("hereeee", schema_i)

        # Load the other polygonGeoJSON.yaml file
    schema_j_path = os.path.join(base_dir, 'polygonGeoJSON.yaml')
    print('Schema j path:', schema_j_path)
    with open(schema_j_path, 'r') as f:
        schema_j = yaml.safe_load(f)
        print("hereeee", schema_j)

        # Load the other multipolygonGeoJSON.yaml file
    schema_k_path = os.path.join(base_dir, 'multipolygonGeoJSON.yaml')
    print('Schema k path:', schema_k_path)
    with open(schema_k_path, 'r') as f:
        schema_k = yaml.safe_load(f)
        print("hereeee", schema_k)

        # Load the other geometrycollectionGeoJSON.yaml file
    schema_l_path = os.path.join(base_dir, 'geometrycollectionGeoJSON.yaml')
    print('Schema l path:', schema_l_path)
    with open(schema_l_path, 'r') as f:
        schema_l = yaml.safe_load(f)
        print("hereeee", schema_l)


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
    # registry = Registry().with_resource(uri=f'file://{base_dir}/', resource=resource)
    print(registry)
    registry = registry.crawl()
    print(registry)

    print('here is the schema for validator', schema_a)
    validator = Draft202012Validator(schema_a, registry=registry)
    validator.validate(instance)

def est_feature_collection_single_item(url):

    # test with url: https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections/climate-normals/items/1664.62.1?f=json

    response = requests.get(url, verify="/etc/ssl/certs")

    instance = response.json()

    assert response.status_code == 200

    # Define the base directory
    base_dir = os.path.abspath('tests/test-files/schemasFeat')
    print('Base dir:', base_dir)


    # Load the other featureGeoJSON.yaml file
    schema_b_path = os.path.join(base_dir, 'featureGeoJSON.yaml')
    print('Schema b path:', schema_b_path)
    with open(schema_b_path, 'r') as f:
        schema_b = yaml.safe_load(f)
        print("hereeee", schema_b)

    # Load the other link.yaml file
    schema_c_path = os.path.join(base_dir, 'link.yaml')
    print('Schema c path:', schema_c_path)
    with open(schema_c_path, 'r') as f:
        schema_c = yaml.safe_load(f)
        print("hereeee", schema_c)

    # Load the other linkBase.yaml file
    schema_d_path = os.path.join(base_dir, 'linkBase.yaml')
    print('Schema d path:', schema_d_path)
    with open(schema_d_path, 'r') as f:
        schema_d = yaml.safe_load(f)
        print("hereeee", schema_d)

    # Load the other geometryGeoJSON.yaml file
    schema_e_path = os.path.join(base_dir, 'geometryGeoJSON.yaml')
    print('Schema e path:', schema_e_path)
    with open(schema_e_path, 'r') as f:
        schema_e = yaml.safe_load(f)
        print("hereeee", schema_e)

        # Load the other pointGeoJSON.yaml file
    schema_f_path = os.path.join(base_dir, 'pointGeoJSON.yaml')
    print('Schema f path:', schema_f_path)
    with open(schema_f_path, 'r') as f:
        schema_f = yaml.safe_load(f)
        print("hereeee", schema_f)

        # Load the other multipointGeoJSON.yaml file
    schema_g_path = os.path.join(base_dir, 'multipointGeoJSON.yaml')
    print('Schema g path:', schema_g_path)
    with open(schema_g_path, 'r') as f:
        schema_g = yaml.safe_load(f)
        print("hereeee", schema_g)

        # Load the other linestringGeoJSON.yaml file
    schema_h_path = os.path.join(base_dir, 'linestringGeoJSON.yaml')
    print('Schema h path:', schema_h_path)
    with open(schema_h_path, 'r') as f:
        schema_h = yaml.safe_load(f)
        print("hereeee", schema_h)

        # Load the other multilinestringGeoJSON.yaml file
    schema_i_path = os.path.join(base_dir, 'multilinestringGeoJSON.yaml')
    print('Schema i path:', schema_i_path)
    with open(schema_i_path, 'r') as f:
        schema_i = yaml.safe_load(f)
        print("hereeee", schema_i)

        # Load the other polygonGeoJSON.yaml file
    schema_j_path = os.path.join(base_dir, 'polygonGeoJSON.yaml')
    print('Schema j path:', schema_j_path)
    with open(schema_j_path, 'r') as f:
        schema_j = yaml.safe_load(f)
        print("hereeee", schema_j)

        # Load the other multipolygonGeoJSON.yaml file
    schema_k_path = os.path.join(base_dir, 'multipolygonGeoJSON.yaml')
    print('Schema k path:', schema_k_path)
    with open(schema_k_path, 'r') as f:
        schema_k = yaml.safe_load(f)
        print("hereeee", schema_k)

        # Load the other geometrycollectionGeoJSON.yaml file
    schema_l_path = os.path.join(base_dir, 'geometrycollectionGeoJSON.yaml')
    print('Schema l path:', schema_l_path)
    with open(schema_l_path, 'r') as f:
        schema_l = yaml.safe_load(f)
        print("hereeee", schema_l)


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
    # registry = Registry().with_resource(uri=f'file://{base_dir}/', resource=resource)
    print(registry)
    registry = registry.crawl()
    print(registry)

    print('here is the schema for validator', schema_b)
    validator = Draft202012Validator(schema_b, registry=registry)
    validator.validate(instance)

def test_feature(url):
    #test with this url:  https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections?f=json

    response = requests.get(url, verify="/etc/ssl/certs")

    instance = response.json()

    assert response.status_code == 200

    print(json.dumps(instance, indent=4))
    print(instance['collections'][0]['title'])

    for collection in instance['collections']:
        if 'itemType' in collection and collection['itemType'] == 'feature':
            print(collection['id'])
            url1 = f"https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections/{collection['id']}?f=json"
            url2 = f"https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections/{collection['id']}/items?limit=1&f=json"

            try:

                response2 = requests.get(url2, verify="/etc/ssl/certs")

                instance2 = response2.json()
                print(url1)
                itemId = instance2['features'][0]['id']

            except Exception as e:
                # Catch any exception that occurs and handle it here
                print(f"An error occurred: {e}")

            url3 = f"https://geomet-dev-31-nightly.edc-mtl.ec.gc.ca/msc-pygeoapi/collections/{collection['id']}/items/{itemId}?f=json"

            print(url1)
            print(url2)
            print(url3)
            print('----------------')
            print(itemId)
            print('----------------')
            est_feature_collection_root(url1)
            est_feature_collection_items(url2)
            est_feature_collection_single_item(url3)


