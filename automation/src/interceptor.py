import requests

from lxml import etree, html

from utility import instrumentation_service_base_url

"""
Interceptor module

Utilizes the selenium wire module to intercept and inspect network traffic.
"""


class NetworkInterceptor:
    """NetworkInterceptor class

    Provides methods to intercept network requests to instrument files before they are sent to the browser
    or abort outgoing requests with a certain structure.
    """

    def __init__(self, web_driver) -> None:
        self.__driver = web_driver

    def instrument_files(self) -> None:
        """Start file instrumentation.
        All files requested by the browser are checked, instrumented if necessary and sent to the browser.
        """
        self.__driver.response_interceptor = self.__file_interceptor

    def __file_interceptor(self, request, response):
        """Intercept network responses and alter response contents to allow for dynamic analysis.

        JavaScript files are sent to the instrumentation service to add statements for dynamic analysis.
        For each HTML file a script tag is added to enable access of common methods for dynamic analysis.
        """
        content_type = response.headers['Content-Type']
        if content_type == None:
            return

        if content_type.startswith('application/javascript'):
            if request.url == f'{instrumentation_service_base_url}/static/script.js':
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
        """Send JavaScript file to the instrumentation service and return instrumented content."""

        name = request.url.split("/")[-1]
        body_string = self.__decode_body(response.body)

        data = {'name': name, 'source': body_string}
        res = requests.post(
            f'{instrumentation_service_base_url}/instrument', data)
        return res.content

    def __handle_html_file(self, response) -> bytes:
        """Add script tag with common functions to HTML file body and return new content."""

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
            f'<script src="{instrumentation_service_base_url}/static/script.js"></script>')

        html_body.append(script_tag)
        return html.tostring(html_ast, pretty_print=True)

    def __decode_body(self, body) -> str:
        """Decode an utf-8 encoded request body to a string and return the result."""

        try:
            body_string = body.decode('utf-8')
        except UnicodeDecodeError:
            # TODO
            return

        return body_string


class ResponseInspector:
    """ResponseInspector class

    Provides methods to inspect the response of the application.
    """

    def __init__(self, web_driver) -> None:
        self.__driver = web_driver
