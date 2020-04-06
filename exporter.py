from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from http import HTTPStatus
from urllib.parse import urlsplit, parse_qs
from consumer import Consumer
from socketserver import TCPServer

ENC = "utf-8"
h_ssl_tls_version_info = "# HELP ssl_tls_version_info The TLS version used\n".encode(ENC)
h_ssl_cert_not_after = "# HELP ssl_cert_not_after NotAfter expressed as a Unix Epoch Time\n".encode(ENC)
h_ssl_cert_not_before = "# HELP ssl_cert_not_before NotBefore expressed as a Unix Epoch Time\n".encode(ENC)
h_ssl_tls_connect_success = "# HELP t_ssl_tls_connect_success connect successfully\n".encode(ENC)
#
t_ssl_tls_version_info = "# TYPE ssl_tls_version_info gauge\n".encode(ENC)
t_ssl_cert_not_after = "# TYPE ssl_cert_not_after gauge\n".encode(ENC)
t_ssl_cert_not_before = "# TYPE ssl_cert_not_before gauge\n".encode(ENC)
t_ssl_tls_connect_success = "# TYPE t_ssl_tls_connect_success gauge\n".encode(ENC)
#
ssl_tls_version_info = "ssl_tls_version_info{version=\"%s\"} 1\n"
ssl_cert_not_after = "ssl_cert_not_after{cn=\"%s\",dnsnames=\"%s\",sn=\"%s\"} %d\n"
ssl_cert_not_before = "ssl_cert_not_before{cn=\"%s\",dnsnames=\"%s\",sn=\"%s\"} %d\n"
ssl_tls_connect_success = "ssl_tls_connect_success %0.0f\n"
#
missingTarget = "missing target\n\n".encode(ENC)
contentType = "Content-Type"
typePrometheus = "text/plain;version=0.0.4"
NL = bytes("\n", ENC)


__author__ = "Marcel Hillmann"
__version__ = "1.0"
__license__ = "GNU GPLv3"


class Exporter(BaseHTTPRequestHandler, ThreadingHTTPServer):

    def __enter__(self):
        """to enable auto close """
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        """to enable auto close """
        pass

    def do_GET(self):
        if self.path == "/favicon.ico":
            self.favicon()
        elif "/metrics" in self.path:
            q = parse_qs(urlsplit(self.path).query)
            target = q.get("target")

            if target is None:
                self.target_missing()
            else:
                self.send_response(HTTPStatus.OK)
                self.send_header(contentType, typePrometheus)
                self.end_headers()

                consumer = Consumer(target)

                success = 0
                if consumer.load():
                    success = 1
                    sn = consumer.serial_number()
                    subject = consumer.subject()
                    san = consumer.alternative_name()
                    not_before = consumer.not_before()
                    not_after = consumer.not_after()

                    self.metric_write(h_ssl_tls_version_info, t_ssl_tls_version_info,
                                      ssl_tls_version_info % consumer.version())
                    self.metric_write(h_ssl_cert_not_after, t_ssl_cert_not_after,
                                      ssl_cert_not_after % (subject, san, sn, not_after))
                    self.metric_write(h_ssl_cert_not_before, t_ssl_cert_not_before,
                                      ssl_cert_not_before % (subject, san, sn, not_before))
                # if load
                self.metric_write(h_ssl_tls_connect_success, t_ssl_tls_connect_success,
                                  ssl_tls_connect_success % success)
                self.wfile.write(NL)
            # if target is None
        elif self.path is "/":
            self.main_page()
        else:
            self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)
            self.end_headers()
        # if self.path
        # do_GET

    def log_message(self, fmt, *args):
        """disable the default behavior"""
        pass
        # log_message

    def log_error(self, fmt, *args):
        """disable the default behavior"""
        pass
        # log_error

    def metric_write(self, metric_help, metric_type, sample):
        self.wfile.write(metric_help)
        self.wfile.write(metric_type)
        self.wfile.write(bytes(sample, ENC))
        # metric_write

    def favicon(self):
        self.send_response(HTTPStatus.NOT_FOUND)
        self.end_headers()
        # favicon

    def version_string(self):
        return "ssl_exporter/1.0"
        # version_string

    def main_page(self):
        self.send_response(HTTPStatus.OK)
        self.send_header(contentType, "text/html")
        self.end_headers()
        self.wfile.write(("<html>\n" +
                          "\t<body>\n" +
                          "\t\t<a href='/metrics'>Metrics</a>\n" +
                          "\t</body>\n" +
                          "</html>\n").encode(ENC))
        # main_page

    def target_missing(self):
        self.send_response(HTTPStatus.BAD_REQUEST)
        self.send_header(contentType, typePrometheus)
        self.end_headers()
        self.wfile.write(missingTarget)
        # target_missing
    # class

if __name__ == "__main__":
    handler = Exporter
    with TCPServer(("", 9000), handler) as httpd:
        print("serving at port 9000")
        httpd.serve_forever()
        # with TCPServer
    print("Server stopped.")
    # __name__ == __main__