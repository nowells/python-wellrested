#############################
# python-wellrested
# A Simple RESTful client
#############################

Introduction
============

The python-wellrested library is a lean client for performing RESTful API calls.

Basic Usage
===========

Basic usage of the python-wellrested library is simple.

To work with a RESTful API you first instantiate the client:

>>> j = JsonRestClient('http://example.com/api/', username='user', pass='password')

Then you can read data using the ``get`` method:

>>> j.get('resource.json')

A response object will be returned with data similar to the following::

<Response 200: {'content': '[\n    {\n        "content": "demo content", \n        "user": {\n            "username": "demouser", \n            "first_name": "Jane"\n        }\n    }, \n    }\n]', 'headers': {'status': '200', 'content-location': u'http://example.com/api/resource.json', 'vary': 'Authorization', 'server': 'Werkzeug/0.5.1 Python/2.5.1', 'connection': 'close', 'date': 'Thu, 06 Aug 2009 13:48:47 GMT', 'content-type': 'application/json; charset=utf-8'}, 'data': None, 'status_code': 200}>

Obviously the exact structure of the data depends on the API that is being called.

To post data to a RESTful API, the ``post`` method is used:

>>> mydata = {'foo':'bar',}
>>> j.post('resource.json', data=mydata)

This will return a response similar to the one above, containing whatever confirmation the remote API delivers upon posting data. This is normally used for creating objects using the remote API.

To put data to a RESTful API, the ``put`` method is used:

>>> mydata = {'foo':'bar_edited',}
>>> j.put('resource.json', data=mydata)

And, finally, to delete data using a RESTful API, the ``delete`` method is used:

>>> j.delete('resource.json)

.. note::

    Please remember that the workings of each RESTful API will vary, and this client only handles the connection between your application and a RESTful resource. The above examples represent the basic usage concepts of python-wellrested, but are not exhaustive nor are they suitable for direct use as doctests.
