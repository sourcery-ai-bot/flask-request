import requests
import urllib3


class RequestsSession(object):
    default_retry_codes = (429, 500, 502, 503, 504)
    headers = {'User-Agent': 'flask_request / 1.0.0',
               'Content-Type': 'application/json',
               'Accept': 'application/json'}

    def __init__(self, app=None, retries=3, backoff_factor=0.5,
                 status_forcelist=()):
        self.status_forcelist = status_forcelist or self.default_retry_codes
        self.backoff_factor = backoff_factor
        self.retries = retries

        self.session = requests.Session()
        retry = urllib3.Retry(
            status=self.retries,
            backoff_factor=self.backoff_factor,
            status_forcelist=self.status_forcelist)

        adapter = requests.adapters.HTTPAdapter(max_retries=retry)

        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        self.session.headers.update(self.headers)

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        if not hasattr(app, 'extensions'):
            app.extensions = {}
            app.extensions['request'] = self

    def http_fetch(self, url, method='GET', headers={}, data=None, timeout=3):
        try:
            response = self.session.request(url=url,
                                            method=method,
                                            headers=headers,
                                            data=data,
                                            timeout=timeout)
        except requests.exceptions.RetryError as error:
            response = requests.Response()
            response.status_code = 500
            response.reason = "MAX RETRIES"
            response._content = b'{}'

        return response
