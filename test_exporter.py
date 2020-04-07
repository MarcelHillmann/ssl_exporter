import unittest
from unittest.mock import MagicMock
from test.support import captured_stdout, captured_stderr
from exporter import Exporter
from io import BytesIO

utf = "utf-8"
ASSERT_MAIN_PAGE = "HTTP/1.0 200 OK\r\n" \
                   "Server: ssl_exporter/1.0\r\n" \
                   "Date: unittest\r\n" \
                   "Content-Type: text/html\r\n\r\n" \
                   "<html>\n\t<body>\n\t\t<a href='/metrics'>Metrics</a>\n\t</body>\n</html>\n".encode(utf)
ASSERT_FAVICON = "HTTP/1.0 404 Not Found\r\n" \
                 "Server: ssl_exporter/1.0\r\n" \
                 "Date: unittest\r\n\r\n".encode(utf)
ASSERT_FOOBAR = "HTTP/1.0 500 Internal Server Error\r\n" \
                "Server: ssl_exporter/1.0\r\n" \
                "Date: unittest\r\n\r\n".encode(utf)
ASSERT_MISSING_TARGET = "HTTP/1.0 400 Bad Request\r\n" \
                        "Server: ssl_exporter/1.0\r\n" \
                        "Date: unittest\r\n" \
                        "Content-Type: text/plain;version=0.0.4\r\n\r\n" \
                        "missing target\n\n".encode(utf)
ASSERT_INVALID_TARGET = "HTTP/1.0 200 OK\r\n" \
                        "Server: ssl_exporter/1.0\r\n" \
                        "Date: unittest\r\n" \
                        "Content-Type: text/plain;version=0.0.4\r\n\r\n" \
                        "# HELP t_ssl_tls_connect_success connect successfully\n" \
                        "# TYPE t_ssl_tls_connect_success gauge\n" \
                        "ssl_tls_connect_success 0\n\n".encode(utf)
ASSERT_VALID_TARGET = "HTTP/1.0 200 OK\r\n" \
                      "Server: ssl_exporter/1.0\r\n" \
                      "Date: unittest\r\n" \
                      "Content-Type: text/plain;version=0.0.4\r\n\r\n" \
                      "# HELP ssl_tls_version_info The TLS version used\n" \
                      "# TYPE ssl_tls_version_info gauge\n" \
                      "ssl_tls_version_info{version=\"TLSv1.3\"} 1\n" \
                      "ssl_tls_version_info{version=\"HTTPS\"} 1\n" \
                      "# HELP ssl_cert_not_after NotAfter expressed as a Unix Epoch Time\n" \
                      "# TYPE ssl_cert_not_after gauge\n" \
                      "ssl_cert_not_after{cn=\"www.google.de\",dnsnames=\"\",sn=\"4f:a4:55:79:93:34:ed:15:08:00:00:00:00:32:0b:f5\"} 1590479943\n" \
                      "# HELP ssl_cert_not_before NotBefore expressed as a Unix Epoch Time\n" \
                      "# TYPE ssl_cert_not_before gauge\n" \
                      "ssl_cert_not_before{cn=\"www.google.de\",dnsnames=\"\",sn=\"4f:a4:55:79:93:34:ed:15:08:00:00:00:00:32:0b:f5\"} 1583225943\n" \
                      "# HELP t_ssl_tls_connect_success connect successfully\n" \
                      "# TYPE t_ssl_tls_connect_success gauge\n" \
                      "ssl_tls_connect_success 1\n\n".encode(utf)


class TestCaseExporter(unittest.TestCase):

    def test_log_message(self):
        """don't show a HTTPServer log message"""

        e = Exporter
        r = MockRequest("")
        with Exporter(r, ("", 65536), e) as handler:
            with captured_stdout() as stdout, captured_stderr() as stderr:
                e.log_message(handler, fmt="log message")
            # capture
        # Exporter
        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(stderr.getvalue(), "")
        # test_log_message

    def test_log_error(self):
        """don't show a HTTPServer error message"""
        e = Exporter
        r = MockRequest("")
        with Exporter(r, ("", 65536), e) as handler:
            with captured_stdout() as stdout, captured_stderr() as stderr:
                e.log_error(handler, "test")
            # capture
        #
        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(stderr.getvalue(), "")
        # test_log_error

    def test_main_page(self):
        """test the root page"""
        r = MockRequest("GET /")
        MockServer(Exporter, r)
        self.assertEqual(ASSERT_MAIN_PAGE, r.result())
        # test_main_page

    def test_favicon(self):
        """return a 404 if the favicon is requested"""
        r = MockRequest("GET /favicon.ico")
        MockServer(Exporter, r)
        self.assertEqual(ASSERT_FAVICON, r.result())
        # test_favicon

    def test_foo_bar(self):
        """return a 501 if a invalid URI is requested"""
        r = MockRequest("GET /foo_bar")
        MockServer(Exporter, r)
        self.assertEqual(ASSERT_FOOBAR, r.result())
        # def test_foo_bar

    def test_without_target(self):
        """return a error message, if no target is given"""
        r = MockRequest("GET /metrics")
        MockServer(Exporter, r)
        self.assertEqual(ASSERT_MISSING_TARGET, r.result())

    def test_with_invalid_target(self):
        """return sampels, if a INValid target is given"""
        r = MockRequest("GET /metrics?target=foo-bar:443")
        MockServer(Exporter, r)
        self.assertEqual(ASSERT_INVALID_TARGET, r.result())

    def test_with_valid_target(self):
        """return sampels, if a VALID target is given"""
        r = MockRequest("GET /metrics?target=www.google.de:443")
        MockServer(Exporter, r)
        self.assertEqual(ASSERT_VALID_TARGET, r.result())

    # TestCaseExporter


class MockRequest(object):

    def __init__(self, msg: str):
        self.msg = BytesIO((msg + " HTTP/1.1").encode("utf-8"))
        self.data = "".encode("utf-8")

    def makefile(self, *args, **kwargs) -> BytesIO:
        return self.msg

    def sendall(self, data):
        self.data = self.data + data

    def result(self) -> bytes:
        return self.data
    # class MockRequest


class MockServer(object):
    def __init__(self, handler, request):
        handler.date_time_string = MagicMock(return_value="unittest")
        self.handler = handler(request, ("0.0.0.0", 65536), self)
        # __init__
    # MockServer


if __name__ == '__main__':
    unittest.main()
    # __name___ == __main__
