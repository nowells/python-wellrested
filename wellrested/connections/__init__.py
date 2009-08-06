import base64
import httplib2
import logging
import mimetypes
import mimetools
import urllib
import urlparse

HTTP_STATUS_OK = '200'

logger = logging.getLogger(__name__)

class RestClient(object):
    content_type = None

    def __init__(self, base_url, username=None, password=None, connection_class=None, **kwargs):
        if connection_class is None:
            connection_class = Connection
        self._connection = connection_class(base_url, username, password, **kwargs)

    def get(self, resource, args=None, data=None, headers=None):
        return self._request(resource, 'get', args=args, data=data, headers=headers)

    def put(self, resource, args=None, data=None, headers=None):
        return self._request(resource, 'put', args=args, data=data, headers=headers)

    def delete(self, resource, args=None, data=None, headers=None):
        return self._request(resource, 'delete', args=args, data=data, headers=headers)

    def post(self, resource, args=None, data=None, headers=None):
        return self._request(resource, 'post', args=args, data=data, headers=headers)

    def _request(self, resource, method, args=None, data=None, headers=None):
        response_data = None
        request_body = self._serialize(data)
        response_headers, response_content = self._connection.request(resource, method, args=args, body=request_body, headers=headers, content_type=self.content_type)
        if response_headers.get('status') == HTTP_STATUS_OK:
            response_data = self._deserialize(response_content)
        return Response(response_headers, response_content, response_data)

    def _serialize(self, data):
        return unicode(data)

    def _deserialize(self, data):
        return unicode(data)

class JsonRestClient(RestClient):
    content_type = 'application/json'

    def _serialize(self, data):
        if data:
            import simplejson
            return simplejson.dumps(data)
        return None

    def _deserialize(self, data):
        if data:
            import simplejson
            return simplejson.loads(data)
        return None

class XmlRestClient(RestClient):
    content_type = 'text/xml'

class Response(object):
    def __init__(self, headers, content, data):
        self.headers = headers
        self.content = content
        self.data = data
        self.status_code = int(headers.get('status', '500'))

    def __repr__(self):
        return '<Response %s: %s>' % (self.status_code, self.__dict__)

class BaseConnection(object):
    def __init__(self, base_url, username=None, password=None):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.url = urlparse.urlparse(base_url)
        (scheme, netloc, path, query, fragment) = urlparse.urlsplit(base_url)
        self.scheme = scheme
        self.host = netloc
        self.path = path

    def _get_content_type(self, filename):
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

    def request(self, resource, method="get", args=None, body=None, headers=None, content_type=None):
        raise NotImplementedError

class Connection(BaseConnection):
    def __init__(self, *args, **kwargs):
        cache = kwargs.pop('cache', None)
        timeout = kwargs.pop('cache', None)
        proxy_info = kwargs.pop('proxy_info', None)

        super(Connection, self).__init__(*args, **kwargs)

        self._conn = httplib2.Http(cache=cache, timeout=timeout, proxy_info=proxy_info)
        self._conn.follow_all_redirects = True

        if self.username and self.password:
            self._conn.add_credentials(self.username, self.password)

    def request(self, resource, method, args=None, body=None, headers=None, content_type=None):
        if headers is None:
            headers = {}

        params = None
        path = resource
        headers['User-Agent'] = 'Basic Agent'

        BOUNDARY = mimetools.choose_boundary()
        CRLF = u'\r\n'

        if body:
            if not headers.get('Content-Type', None):
                headers['Content-Type'] = content_type or 'text/plain'
            headers['Content-Length'] = str(len(body))
        else:
            if headers.has_key('Content-Length'):
                del headers['Content-Length']

            headers['Content-Type'] = 'text/plain'

            if args:
                if method == "get":
                    path += u"?" + urllib.urlencode(args)
                elif method == "put" or method == "post":
                    headers['Content-Type'] = 'application/x-www-form-urlencoded'
                    body = urllib.urlencode(args)

        request_path = []
        # Normalise the / in the url path
        if self.path != "/":
            if self.path.endswith('/'):
                request_path.append(self.path[:-1])
            else:
                request_path.append(self.path)
            if path.startswith('/'):
                request_path.append(path[1:])
            else:
                request_path.append(path)

        response_headers, response_content = self._conn.request(u"%s://%s%s" % (self.scheme, self.host, u'/'.join(request_path)), method.upper(), body=body, headers=headers)
        return response_headers, response_content

