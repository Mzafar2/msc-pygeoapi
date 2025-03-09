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
import os

@pytest.fixture()
def url(pytestconfig):
    return pytestconfig.getoption('url')


def test_msc_pygeoapi_service_online(url):

    # Define the base directory
    base_dir = os.path.abspath('tests/test-files/schemas/common-geodata')
    print('Base dir:', base_dir)

    # Load the schema_a.yaml file (in dir_a)
    schema_a_path = os.path.join(base_dir, 'collectionDesc.yaml')
    print('Schema a path:', schema_a_path)
    with open(schema_a_path, 'r') as f:
        schema_a = yaml.safe_load(f)
        print("hereeee", schema_a)

    # Load the other schema_b.yaml file (in dir_b)
    schema_b_path = os.path.join(base_dir, '../common-core/link.yaml')
    print('Schema b path:', schema_b_path)
    with open(schema_b_path, 'r') as f:
        schema_b = yaml.safe_load(f)
        print("hereeee", schema_b)

    # Load the other schema_c.yaml file (in dir_c)
    schema_c_path = os.path.join(base_dir, 'extent-uad.yaml')
    print('Schema c path:', schema_c_path)
    with open(schema_c_path, 'r') as f:
        schema_c = yaml.safe_load(f)
        print("hereeee", schema_c)

    # Load the other schema_d.yaml file (in dir_d)
    schema_d_path = os.path.join(base_dir, 'extent.yaml')
    print('Schema d path:', schema_d_path)
    with open(schema_d_path, 'r') as f:
        schema_d = yaml.safe_load(f)
        print("hereeee", schema_d)



    # resource for schema a
    resourceA = Resource(contents=schema_a, specification=jsonschema.DRAFT202012)
    # resource for schema b
    resourceB = Resource(contents=schema_b, specification=jsonschema.DRAFT202012)
    # resource for schema c
    resourceC = Resource(contents=schema_c, specification=jsonschema.DRAFT202012)
    # resource for schema c
    resourceD = Resource(contents=schema_d, specification=jsonschema.DRAFT202012)

    registry = Registry().with_resources([(f'{base_dir}', resourceA), ('../common-core/link.yaml', resourceB), ('extent-uad.yaml', resourceC), ('extent.yaml', resourceD)])

    # Register the schema a in the registry as a resource
    # registry = Registry().with_resource(uri=f'file://{base_dir}/', resource=resource)
    print(registry)
    registry = registry.crawl()
    print(registry)

    print(registry.contents(f'{base_dir}'))


    validator = Draft202012Validator(schema_a, registry=registry)


    # Example instance to validate
    # Make a basic request at the URL
    # response = requests.get(url, verify="/etc/ssl/certs")
    # instance = response.json()

    instance = {
        "id":"icoads-sst",
        "title":"International Comprehensive Ocean-Atmosphere Data Set (ICOADS)",
        "description":"International Comprehensive Ocean-Atmosphere Data Set (ICOADS)",
        "keywords":[
            "icoads",
            "sst",
            "air temperature"
        ],
        "links":[
            {
                "type":"text/html",
                "rel":"canonical",
                "title":"information",
                "href":"https://psl.noaa.gov/data/gridded/data.coads.1deg.html",
                "hreflang":"en-US"
            },
            {
                "type":"application/json",
                "rel":"root",
                "title":"The landing page of this server as JSON",
                "href":"https://demo.pygeoapi.io/stable?f=json"
            },
            {
                "type":"text/html",
                "rel":"root",
                "title":"The landing page of this server as HTML",
                "href":"https://demo.pygeoapi.io/stable?f=html"
            },
            {
                "type":"application/json",
                "rel":"self",
                "title":"This document as JSON",
                "href":"https://demo.pygeoapi.io/stable/collections/icoads-sst?f=json"
            },
            {
                "type":"application/ld+json",
                "rel":"alternate",
                "title":"This document as RDF (JSON-LD)",
                "href":"https://demo.pygeoapi.io/stable/collections/icoads-sst?f=jsonld"
            },
            {
                "type":"text/html",
                "rel":"alternate",
                "title":"This document as HTML",
                "href":"https://demo.pygeoapi.io/stable/collections/icoads-sst?f=html"
            },
            {
                "type":"application/json",
                "rel":"data",
                "title":"position query for this collection as JSON",
                "href":"https://demo.pygeoapi.io/stable/collections/icoads-sst/position?f=json"
            },
            {
                "type":"text/html",
                "rel":"data",
                "title":"position query for this collection as HTML",
                "href":"https://demo.pygeoapi.io/stable/collections/icoads-sst/position?f=html"
            },
            {
                "type":"application/json",
                "rel":"data",
                "title":"cube query for this collection as JSON",
                "href":"https://demo.pygeoapi.io/stable/collections/icoads-sst/cube?f=json"
            },
            {
                "type":"text/html",
                "rel":"data",
                "title":"cube query for this collection as HTML",
                "href":"https://demo.pygeoapi.io/stable/collections/icoads-sst/cube?f=html"
            }
        ],
        "extent":{
            "spatial":{
                "bbox":[
                    [
                        -180,
                        -90,
                        180,
                        90
                    ]
                ],
                "crs":"http://www.opengis.net/def/crs/OGC/1.3/CRS84"
            },
            "temporal":{
                "interval":[
                    [
                        "2000-01-16T06:00:00+00:00",
                        "2000-12-16T06:00:00+00:00"
                    ]
                ],
                "definition": "anything"
            },
            "other":{
                "6":7
            }
        },
        "data_queries":{
            "position":{
                "link":{
                    "href":"https://demo.pygeoapi.io/stable/collections/icoads-sst/position",
                    "rel":"data"
                }
            },
            "cube":{
                "link":{
                    "href":"https://demo.pygeoapi.io/stable/collections/icoads-sst/cube",
                    "rel":"data"
                }
            }
        },
        "parameter_names":{
            "SST":{
                "id":"SST",
                "type":"Parameter",
                "name":"SEA SURFACE TEMPERATURE",
                "unit":{
                    "label":{
                        "en":"SEA SURFACE TEMPERATURE"
                    },
                    "symbol":{
                        "value":"Deg C",
                        "type":"http://www.opengis.net/def/uom/UCUM/"
                    }
                }
            },
            "AIRT":{
                "id":"AIRT",
                "type":"Parameter",
                "name":"AIR TEMPERATURE",
                "unit":{
                    "label":{
                        "en":"AIR TEMPERATURE"
                    },
                    "symbol":{
                        "value":"DEG C",
                        "type":"http://www.opengis.net/def/uom/UCUM/"
                    }
                }
            },
            "UWND":{
                "id":"UWND",
                "type":"Parameter",
                "name":"ZONAL WIND",
                "unit":{
                    "label":{
                        "en":"ZONAL WIND"
                    },
                    "symbol":{
                        "value":"M/S",
                        "type":"http://www.opengis.net/def/uom/UCUM/"
                    }
                }
            },
            "VWND":{
                "id":"VWND",
                "type":"Parameter",
                "name":"MERIDIONAL WIND",
                "unit":{
                    "label":{
                        "en":"MERIDIONAL WIND"
                    },
                    "symbol":{
                        "value":"M/S",
                        "type":"http://www.opengis.net/def/uom/UCUM/"
                    }
                }
            }
        }
    }

    validator.validate(instance)

    # Perform validation, resolving any $ref in the process
    # for error in validator.iter_errors(instance):
    #     print(f"Validation error: {error.message}")
