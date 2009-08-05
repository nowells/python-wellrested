import base64
import httplib2
import mimetypes
import mimetools
import urllib
import urlparse
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class Response(object):
    def __init__(self, headers, content):
        self.headers = headers
        self.content = content

    def __repr__(self):
        return '<Response %s>' % self.__dict__

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

    def get(self, resource, args=None, headers={}):
        return self._request(resource, "get", args, headers=headers)

    def delete(self, resource, args=None, headers={}):
        return self._handle_request(resource, "delete", args, headers=headers)

    def head(self, resource, args=None, headers={}):
        return self._handle_request(resource, "head", args, headers=headers)

    def post(self, resource, args=None, body=None, filename=None, headers={}):
        return self._handle_request(resource, "post", args , body=body, filename=filename, headers=headers)

    def put(self, resource, args=None, body=None, filename=None, headers={}):
        return self._handle_request(resource, "put", args , body=body, filename=filename, headers=headers)

    def _get_content_type(self, filename):
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

    def _handle_request(self, resource, method="get", args=None, body=None, filename=None, headers={}):
        raise NotImplementedError

class Connection(BaseConnection):
    def __init__(self, *args, **kwargs):
        cache = kwargs.pop('cache')
        timeout = kwargs.pop('cache')
        proxy_info = kwargs.pop('proxy_info')

        super(Connection, self).__init__(*args, **kwargs)

        self._conn = httplib2.Http(cache=cache, timeout=timeout, proxy_info=proxy_info)
        self._conn.follow_all_redirects = True

        if self.username and self.password:
            self._conn.add_credentials(self.username, self.password)

    def _handle_request(self, resource, method="get", args=None, body=None, filename=None, headers={}):
        params = None
        path = resource
        headers['User-Agent'] = 'Basic Agent'

        BOUNDARY = mimetools.choose_boundary()
        CRLF = u'\r\n'

        if filename and body:
            content_type = self._get_content_type(filename)
            headers['Content-Type']='multipart/form-data; boundary='+BOUNDARY
            encode_string = StringIO()
            encode_string.write(CRLF)
            encode_string.write(u'--' + BOUNDARY + CRLF)
            encode_string.write(u'Content-Disposition: form-data; name="file"; filename="%s"' % filename)
            encode_string.write(CRLF)
            encode_string.write(u'Content-Type: %s' % content_type + CRLF)
            encode_string.write(CRLF)
            encode_string.write(body)
            encode_string.write(CRLF)
            encode_string.write(u'--' + BOUNDARY + u'--' + CRLF)

            body = encode_string.getvalue()
            headers['Content-Length'] = str(len(body))
        elif body:
            if not headers.get('Content-Type', None):
                headers['Content-Type']='text/xml'
            headers['Content-Length'] = str(len(body))
        else:
            if headers.has_key('Content-Length'):
                del headers['Content-Length']

            headers['Content-Type']='text/plain'

            if args:
                if method == "get":
                    path += u"?" + urllib.urlencode(args)
                elif method == "put" or method == "post":
                    headers['Content-Type']='application/x-www-form-urlencoded'
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

        resp, content = self._conn.request(u"%s://%s%s" % (self.scheme, self.host, u'/'.join(request_path)), method.upper(), body=body, headers=headers)
        # TODO trust the return encoding type in the decode?
        return Response(resp, content)
