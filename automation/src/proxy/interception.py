import requests
import urllib.parse

from lxml import etree, html
from requests_toolbelt.multipart import decoder
from selenium.webdriver import Chrome
from seleniumwire.request import Request, Response
from typing import List

from src.utility.helpers import service_base_url, instrumentation_controller

"""
Proxy module

Utilizes the selenium wire module to intercept and inspect network traffic.
"""

submission_interception_header = "Successful-Form-Submission"


class NetworkInterceptor:
    """NetworkInterceptor class

    Provides methods to intercept network requests to instrument files before they are sent to the browser
    or abort outgoing requests with a certain structure.
    """

    def __init__(self, web_driver: Chrome) -> None:
        self.__allowed_urls = None
        self.__driver = web_driver
        self.generated_values: List[str] = []

    def delete_request_interceptor(self) -> None:
        del self.__driver.request_interceptor

    def delete_repsonse_interceptor(self) -> None:
        del self.__driver.response_interceptor

    def instrument_files(self) -> None:
        """Start file instrumentation.

        All files requested by the browser are checked, instrumented if necessary and sent to the browser.
        """
        del self.__driver.response_interceptor
        self.__driver.response_interceptor = self.__file_interceptor

    # For Evaluation only?
    def block_all_outgoing_requests(
        self, allowed_urls: List[str] | None = None
    ) -> None:
        del self.__driver.request_interceptor
        if allowed_urls is not None:
            self.__allowed_urls = allowed_urls
        self.__driver.request_interceptor = self.__all_request_blocker

    def scan_for_form_submission(self) -> None:
        self.__request_scanner = RequestScanner()
        del self.__driver.request_interceptor
        self.__driver.request_interceptor = self.__form_submission_interceptor

    def __file_interceptor(self, request: Request, response: Response) -> None:
        """Intercept network responses and alter response contents to allow for dynamic analysis.

        JavaScript files are sent to the instrumentation service to add statements for dynamic analysis.

        For each HTML file a script tag is added to enable access of common methods for dynamic analysis.
        """
        content_type = response.headers["Content-Type"]
        if content_type == None:
            return

        if content_type.startswith("application/javascript"):
            if request.url.startswith(f"{service_base_url}/static/"):
                return

            response.body = self.__handle_js_file(request, response)

        if content_type.startswith("text/html"):
            response.body = self.__handle_html_file(response)

        # Set correct new content length header
        content_length = response.headers.get("content-length")
        if content_length:
            del response.headers["content-length"]
            response.headers["content-length"] = str(len(response.body))

    def __handle_js_file(self, request: Request, response: Response) -> bytes:
        """Send JavaScript file to the instrumentation service and return instrumented content."""

        name = request.url.split("/")[-1]
        body_string = decode_bytes(response.body)

        data = {"name": name, "source": body_string}
        res = requests.post(f"{instrumentation_controller}/instrument", data)
        return res.content

    def __handle_html_file(self, response: Response) -> bytes:
        """Add script tag with common functions to HTML file body and return new content."""

        try:
            body_string = decode_bytes(response.body)
            html_ast = html.fromstring(body_string)
            html_body = html_ast.find(".//body")
        except Exception:
            # TODO
            return response.body

        if html_body == None:
            return

        record_script_tag = etree.fromstring(
            f'<script src="{service_base_url}/static/record.js"></script>'
        )

        html_body.append(record_script_tag)
        return html.tostring(html_ast, pretty_print=True)

    def __form_submission_interceptor(self, request: Request) -> None:
        if self.__request_scanner.all_values_in_form_request(
            request, self.generated_values
        ):
            self.__stop_request(request)

    def __all_request_blocker(self, request: Request) -> None:
        if (
            service_base_url not in request.url
            and self.__allowed_urls is not None
            and request.url not in self.__allowed_urls
        ):
            self.__stop_request(request)

    def __stop_request(self, request):
        request.create_response(
            status_code=202,
            headers={
                "Content-Type": "application/json",
                submission_interception_header: "true",
            },
            body=b"{}",
        )


class RequestScanner:
    def all_values_in_form_request(
        self, request: Request, generated_values: List[str]
    ) -> bool:
        self.generated_values = generated_values

        if request.method != "GET" and request.method != "POST":
            return False

        if request.method == "GET":
            return self.__scan_for_values_in_url(request)
        elif request.method == "POST":
            content_type = str(request.headers["Content-Type"])

        if content_type.startswith("application/x-www-form-urlencoded"):
            return self.__scan_for_values_in_urlencoded_form_data(request)
        elif content_type.startswith("multipart/form-data"):
            return self.__scan_for_values_in_multipart_form_data(request, content_type)
        elif content_type.startswith("text/plain"):
            return self.__scan_for_values_in_plain_text(request)
        else:
            return self.__scan_for_values(request)

    def __scan_for_values_in_url(self, request: Request) -> bool:
        return self.__all_values_in_query_string(request.querystring)

    def __scan_for_values_in_urlencoded_form_data(self, request: Request) -> bool:
        body = decode_bytes(request.body)
        return self.__all_values_in_query_string(body)

    def __scan_for_values_in_multipart_form_data(
        self, request: Request, content_type: str
    ) -> bool:
        elements = decoder.MultipartDecoder(request.body, content_type).parts
        values = list(map(lambda e: e.text, elements))

        return set(values) == set(self.generated_values)

    def __scan_for_values_in_plain_text(self, request: Request) -> bool:
        body = decode_bytes(request.body)
        elements = body.split("\r\n")
        values = list(map(lambda e: e.split("=", 1)[1] if "=" in e else None, elements))
        values = [v for v in values if v is not None]

        return set(values) == set(self.generated_values)

    def __scan_for_values(self, request: Request) -> bool:
        body = decode_bytes(request.body)
        return all(s in body for s in self.generated_values)

    def __all_values_in_query_string(self, query_string: str) -> bool:
        if "&" not in query_string:
            return False

        vars = query_string.split("&")
        values = list(map(lambda v: v.split("=", 1)[1], vars))
        plain_values = list(map(lambda v: urllib.parse.unquote_plus(v), values))

        return set(plain_values) == set(self.generated_values)


def decode_bytes(body: bytes) -> str:
    """Decode a request body in bytes to an utf-8 string and return the result."""

    try:
        body_string = body.decode("utf-8")
    except UnicodeDecodeError:
        return ""

    return body_string