import json
import requests
import urllib.parse

from lxml import etree, html
from requests_toolbelt.multipart import decoder
from selenium.webdriver import Chrome
from seleniumwire.request import Request, Response
from typing import Dict, List

from src.utility.helpers import (
    split_on_newline,
    service_base_url,
    instrumentation_controller,
)

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
        self.generated_values: Dict[str, str] = {}
        self.__driver = web_driver
        self.__javascript_mime_types = [
            "text/javascript",
            "application/javascript",
            "application/x-javascript",
            "text/javascript1.0",
            "text/javascript1.1",
            "text/javascript1.2",
            "text/javascript1.3",
            "text/javascript1.4",
            "text/javascript1.5",
            "text/jscript",
            "text/livescript",
        ]

        self.html_files_instrumented = 0
        self.js_files_instrumented = 0

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

    def scan_for_form_submission(self) -> None:
        self.__request_scanner = RequestScanner()
        del self.__driver.request_interceptor
        self.__driver.request_interceptor = self.__form_submission_interceptor

    def block_form_submission(self) -> None:
        self.__request_scanner = RequestScanner()
        del self.__driver.request_interceptor
        self.__driver.request_interceptor = self.__form_submission_blocker

    def __file_interceptor(self, request: Request, response: Response) -> None:
        """Intercept network responses and alter response contents to allow for dynamic analysis.

        JavaScript files are sent to the instrumentation service to add statements for dynamic analysis.

        For each HTML file a script tag is added to enable access of common methods for dynamic analysis.
        """

        content_type = response.headers["Content-Type"]
        # print(request, content_type)
        if content_type == None:
            return

        if any(
            content_type.startswith(mime_type)
            for mime_type in self.__javascript_mime_types
        ):
            new_body = self.__handle_js_file(request, response)
            if new_body:
                response.body = new_body
                self.js_files_instrumented += 1

        if content_type.startswith("text/html"):
            new_body = self.__handle_html_file(response)
            if new_body:
                response.body = new_body
                self.html_files_instrumented += 1

        # Set correct new content length header
        content_length = response.headers.get("content-length")
        if content_length:
            del response.headers["content-length"]
            response.headers["content-length"] = str(len(response.body))

    def __handle_js_file(self, request: Request, response: Response) -> bytes:
        """Send JavaScript file to the instrumentation service and return instrumented content."""

        name = request.url.split("/")[-1]
        if "?" in name:
            name = name.split("?")[0]

        if name != "password-strength-indicator.js":
            return

        body_string = decode_bytes(response.body)

        data = {"name": name, "source": body_string}
        res = requests.post(f"{instrumentation_controller}/instrument", data)
        return res.content

    def __handle_html_file(self, response: Response) -> bytes:
        """Optionally adjust existing CSP meta tag and add script tag with common functions to HTML file body and return new content."""

        try:
            body_string = decode_bytes(response.body)
            html_ast = html.fromstring(body_string)
        except Exception:
            return ""

        html_head = html_ast.find(".//head")
        if html_head == None:
            return

        record_script = etree.fromstring(
            """<script>var c989a310_3606_4512_bee4_2bc00a61e8ac = false;
function b0aed879_987c_461b_af34_c9c06fe3ed46(action, args, file, location) {
  if (!c989a310_3606_4512_bee4_2bc00a61e8ac) {
    return;
  }
  var xhr = new XMLHttpRequest();
  xhr.open("POST", "http://localhost:4000/analysis/record", false); // make request synchronous to ensure that all traces arrive at the server before analysis starts
  xhr.setRequestHeader("Content-Type", "application/json");
  xhr.send(
    JSON.stringify({
      action,
      args,
      time: new Date().getTime(),
      file,
      location,
      pageFile: 1,
    })
  );
}</script>"""
        )

        # Add custom script to head
        html_head.insert(0, record_script)
        return html.tostring(html_ast, pretty_print=True)

    def __form_submission_interceptor(self, request: Request) -> None:
        if service_base_url in request.url:
            return

        if len(
            self.generated_values
        ) > 0 and self.__request_scanner.all_values_in_form_request(
            request, self.generated_values
        ):
            self.__fake_response(request)

    def __form_submission_blocker(self, request: Request) -> None:
        if service_base_url in request.url:
            return

        if len(
            self.generated_values
        ) > 0 and self.__request_scanner.all_values_in_form_request(
            request, self.generated_values
        ):
            request.abort()

    def __fake_response(self, request):
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
        self, request: Request, generated_values: Dict[str, str]
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
        elif content_type.startswith("application/json"):
            return self.__scan_for_values_in_json(request)
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
        var_dict = {}
        elements = decoder.MultipartDecoder(request.body, content_type).parts
        for element in elements:
            name = decode_bytes(element.headers[b"Content-Disposition"]).split("=", 1)[
                1
            ]
            name = name.replace('"', "")
            value = element.text
            var_dict[name] = value

        # Check for subset here because there can always be hidden fields with additional, non generated values
        return self.generated_values.items() <= var_dict.items()

    def __scan_for_values_in_plain_text(self, request: Request) -> bool:
        var_dict = {}

        body = decode_bytes(request.body)
        elements = split_on_newline(body)

        for name_var in elements:
            if "=" in name_var:
                name, value = name_var.split("=")
                var_dict[name] = value

        # Check for subset here because there can always be hidden fields with additional, non generated values
        return self.generated_values.items() <= var_dict.items()

    def __scan_for_values_in_json(self, request: Request) -> bool:
        body_str = decode_bytes(request.body)
        body: Dict = json.loads(body_str)

        if isinstance(body, Dict):
            return self.generated_values.items() <= body.items()
        else:
            return False

    def __scan_for_values(self, request: Request) -> bool:
        body = decode_bytes(request.body)
        return all(
            s in body
            for s in [item for pair in self.generated_values.items() for item in pair]
        )

    def __all_values_in_query_string(self, query_string: str) -> bool:
        if "&" not in query_string:
            return False

        var_dict = {}
        name_vars = query_string.split("&")
        for name_var in name_vars:
            if "=" in name_var:
                name, value = name_var.split("=")
                var_dict[urllib.parse.unquote_plus(name)] = urllib.parse.unquote_plus(
                    value
                )

        # Check for subset here because there can always be hidden fields with additional, non generated values
        return self.generated_values.items() <= var_dict.items()


def decode_bytes(body: bytes) -> str:
    """Decode a request body in bytes to an utf-8 string and return the result."""

    try:
        body_string = body.decode("utf-8")
    except UnicodeDecodeError as e:
        # print("UnicodeDecodeError when decoding request body")
        # print(e)
        return ""

    return body_string
