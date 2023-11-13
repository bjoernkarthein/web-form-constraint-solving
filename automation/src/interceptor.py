import requests

from lxml import etree, html

"""
Interceptor module

Utilizes the selenium wire module to intercept and inspect network traffic
"""


class NetworkInterceptor:
    """NetworkInterceptor class

    Provides methods to intercept network requests to instrument files before they are sent to the browser
    or abort outgoing requests with a certain structure.
    """

    def __init__(self, web_driver) -> None:
        self.__driver = web_driver
        self.__instrumentation_service_base_url = 'http://localhost:4000'

    def instrument_files(self) -> None:
        self.__driver.response_interceptor = self.__file_interceptor

    def __file_interceptor(self, request, response):
        content_type = response.headers['Content-Type']
        if content_type == None:
            return

        if content_type.startswith('application/javascript'):
            if request.url == f'{self.__instrumentation_service_base_url}/static/script.js':
                return

            response.body = self.__handle_js_file(request, response)

        if content_type.startswith('text/html'):
            response.body = self.__handle_html_file(response)

        # Set correct new content length header
        content_length = response.headers.get('content-length')
        if content_length:
            del response.headers['content-length']
            response.headers['content-length'] = str(len(response.body))

    def __handle_js_file(self, request, response) -> bytes:
        name = request.url.split("/")[-1]
        body_string = self.__decode_body(response.body)

        data = {'name': name, 'source': body_string}
        res = requests.post(
            f'{self.__instrumentation_service_base_url}/instrument', data)
        return res.content

    def __handle_html_file(self, response) -> bytes:
        try:
            body_string = self.__decode_body(response.body)
            html_ast = html.fromstring(body_string)
            html_body = html_ast.find('.//body')
        except Exception:
            # TODO
            return response.body

        if html_body == None:
            return

        script_tag = etree.fromstring(
            f'<script src="{self.__instrumentation_service_base_url}/static/script.js"></script>')

        html_body.append(script_tag)
        return html.tostring(html_ast, pretty_print=True)

    def __decode_body(self, body) -> str:
        try:
            body_string = body.decode('utf-8')
        except UnicodeDecodeError as e:
            # TODO
            return

        return body_string


class ResponseInspector:
    """ResponseInspector class

    Provides methods to inspect the response of the application.
    """

    def __init__(self, web_driver) -> None:
        self.__driver = web_driver
