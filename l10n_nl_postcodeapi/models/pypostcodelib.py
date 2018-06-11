'''
pyPostcode by Stefan Jansen
pyPostcode is an api wrapper for http://postcodeapi.nu
'''

try:
    from urllib.request import urlopen, Request  # for Python 3
except ImportError:
    from urllib2 import urlopen, Request  # for Python 2

import json
import logging


__version__ = '0.5'


class pyPostcodeException(Exception):

    def __init__(self, id, message):
        self.id = id
        self.message = message


class Api(object):

    def __init__(self, api_key, api_version=(2, 0, 0)):
        if api_key is None or api_key is '':
            raise pyPostcodeException(
                0, "Please request an api key on http://postcodeapi.nu")

        self.api_key = api_key
        self.api_version = api_version
        if api_version >= (2, 0, 0):
            self.url = 'https://postcode-api.apiwise.nl'
        else:
            self.url = 'http://api.postcodeapi.nu'

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

        headers = {
            "Accept": "application/json",
            "Accept-Language": "en",
            # this is the v1 api
            "Api-Key": self.api_key,
            # this is the v2 api
            "X-Api-Key": self.api_key,
        }

        result = urlopen(Request(
            self.url + path, headers=headers,
        ))

        if result.getcode() is not 200:
            self.handleresponseerror(result.getcode())

        resultdata = result.read()

        if isinstance(resultdata, bytes):
            resultdata = resultdata.decode("utf-8")  # for Python 3
        jsondata = json.loads(resultdata)

        if self.api_version >= (2, 0, 0):
            data = jsondata.get('_embedded', {}).get('addresses', [])
            if data:
                data = data[0]
            else:
                data = None
        else:
            data = jsondata['resource']

        return data

    def getaddress(self, postcode, house_number=None):
        if house_number is None:
            house_number = ''

        if self.api_version >= (2, 0, 0):
            path = '/v2/addresses/?postcode={0}&number={1}'
        else:
            path = '/{0}/{1}'
        path = path.format(
            str(postcode),
            str(house_number))

        try:
            data = self.request(path)
        except pyPostcodeException as e:
            logging.error(
                'Error looking up %s%s%s on %s: %d %s',
                postcode, house_number and ' ' or '', house_number, self.url,
                e.id, e.message)
            data = None
        except Exception as e:
            logging.exception(e)
            data = None

        if data is not None:
            return Resource(data)
        else:
            return False


class Resource(object):

    def __init__(self, data):
        self._data = data

    @property
    def street(self):
        return self._data['street']

    @property
    def house_number(self):
        '''
        House number can be empty when postcode search
        is used without house number
        '''
        return self._data.get('number', self._data.get('house_number'))

    @property
    def postcode(self):
        return self._data.get('postcode')

    @property
    def town(self):
        return self._data.get('city', {}).get('label', self._data.get('town'))

    @property
    def municipality(self):
        result = self._data.get('municipality', {})
        if isinstance(result, dict):
            result = result.get('label')
        return result

    @property
    def province(self):
        result = self._data.get('province', {})
        if isinstance(result, dict):
            result = result.get('label')
        return result

    def _get_geo_coordinates(self, geo_type):
        return self._data.get('geo', {}).get('center', {}).get(geo_type)\
            .get('coordinates', [None, None])

    @property
    def latitude(self):
        if self._data.get('latitude'):
            return self._data.get('latitude')
        return self._get_geo_coordinates('wgs84')[1]

    @property
    def longitude(self):
        if self._data.get('longitude'):
            return self._data.get('longitude')
        return self._get_geo_coordinates('wgs84')[0]

    @property
    def x(self):
        if self._data.get('x'):
            return self._data.get('x')
        return self._get_geo_coordinates('rd')[0]

    @property
    def y(self):
        if self._data.get('y'):
            return self._data.get('y')
        return self._get_geo_coordinates('rd')[1]
