#!/usr/bin/python
# -*- coding: utf-8 -*-


'''
pyPostcode by Stefan Jansen
pyPostcode is an api wrapper for http://postcodeapi.nu
'''


import httplib
import json


__version__ = '0.1'


class pyPostcodeException(Exception):

    def __init__(self, id, message):
        self.id = id
        self.message = message


class Api(object):

    def __init__(self, api_key):
        if api_key is None or api_key is '':
            raise pyPostcodeException(0, "Please request an api key on http://postcodeapi.nu")

        self.api_key = api_key
        self.url = 'api.postcodeapi.nu'

    def handleresponseerror(self, status):
        if status == 401:
            msg = "Access denied! Api-key missing or invalid"
        elif status == 404:
            msg = "No result found"
        elif status == 500:
            msg = "Unknown API error"
        else:
            msg = "dafuq?"

        raise pyPostcodeException(status, msg)

    def request(self, path=None):
        '''Helper function for HTTP GET requests to the API'''

        headers = {"Content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                   "Accept": "application/json",
                   "Accept-Language": "en",
                   "Api-Key": self.api_key}

        conn = httplib.HTTPConnection(self.url)
        '''Only GET is supported by the API at this time'''
        conn.request('GET', path, None, headers)

        result = conn.getresponse()

        if result.status is not 200:
            conn.close()
            self.handleresponseerror(result.status)

        resultdata = result.read()
        conn.close()

        jsondata = json.loads(resultdata)
        data = jsondata['resource']

        return data

    def getaddress(self, postcode, house_number=None):
        if house_number == None:
            house_number = ''

        path = '/{0}/{1}'.format(
            str(postcode),
            str(house_number))

        try:
            data = self.request(path)
        except Exception:
            data = None

        if data is not None:
            return Resource(data)
        else:
            return False


class Resource(object):

    def __init__(self, data):
        self._street = None
        self._house_number = None
        self._postcode = None
        self._town = None
        self._municipality = None
        self._province = None
        self._latitude = None
        self._longitude = None
        self._x = None
        self._y = None

        if data is not None:
            self.setdata(data)


    def setdata(self, data):
        self._data = data
        data_keys = self._data.keys()
        for key in data_keys:
            if hasattr(self, key):
                setattr(self, key, self._data[key])

    @property
    def street(self):
        return self._street
    @street.setter
    def street(self, value):
        self._street = value

    @property
    def house_number(self):
        '''
        House number can be empty when postcode search
        is used without house number
        '''
        return self._house_number
    @house_number.setter
    def house_number(self, value):
        self._house_number = value

    @property
    def postcode(self):
        return self._postcode
    @postcode.setter
    def postcode(self, value):
        self._postcode = value

    @property
    def town(self):
        return self._town
    @town.setter
    def town(self, value):
        self._town = value

    @property
    def municipality(self):
        return self._municipality
    @municipality.setter
    def municipality(self, value):
        self._municipality = value

    @property
    def province(self):
        return self._province
    @province.setter
    def province(self, value):
        self._province = value

    @property
    def latitude(self):
        return self._latitude
    @latitude.setter
    def latitude(self, value):
        self._latitude = value

    @property
    def longitude(self):
        return self._longitude
    @longitude.setter
    def longitude(self, value):
        self._longitude = value

    @property
    def x(self):
        return self._x
    @x.setter
    def x(self, value):
        self._x = value

    @property
    def y(self):
        return self._y
    @y.setter
    def y(self, value):
        self._y = value

