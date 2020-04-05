from http.server import SimpleHTTPRequestHandler
import http.client
from http import HTTPStatus
from datetime import datetime
from urllib.parse import urlsplit, parse_qs, urlparse
import time
import traceback

ENC = "utf-8"
ssl_tls_version_info = "ssl_tls_version_info{version=\"%s\"} 1\n"
h_ssl_tls_version_info = bytes("# HELP ssl_tls_version_info The TLS version used\n", ENC)
t_ssl_tls_version_info = bytes("# TYPE ssl_tls_version_info gauge\n", ENC)
ssl_cert_not_after = "ssl_cert_not_after{cn=\"%s\",dnsnames=\"%s\",sn=\"%s\"} %d\n"
h_ssl_cert_not_after = bytes("# HELP ssl_cert_not_after NotAfter expressed as a Unix Epoch Time\n", ENC)
t_ssl_cert_not_after = bytes("# TYPE ssl_cert_not_after gauge\n", ENC)
ssl_cert_not_before = "ssl_cert_not_before{cn=\"%s\",dnsnames=\"%s\",sn=\"%s\"} %d\n"
h_ssl_cert_not_before = bytes("# HELP ssl_cert_not_before NotBefore expressed as a Unix Epoch Time\n", ENC)
t_ssl_cert_not_before = bytes("# TYPE ssl_cert_not_before gauge\n", ENC)
ssl_tls_connect_success = "ssl_tls_connect_success %0.0f\n"
h_ssl_tls_connect_success = bytes("# HELP ssl_tls_version_info The TLS version used\n", ENC)
t_ssl_tls_connect_success = bytes("# TYPE ssl_tls_version_info gauge\n", ENC)
NL = bytes("\n", ENC)


class Exporter(SimpleHTTPRequestHandler):
    server_version = "ssl_exporter"

    def do_GET(self):
        if self.path == "/favicon.ico":
            self.send_response(HTTPStatus.NOT_FOUND)
            self.end_headers()

            self.log_error()
            return
        # self.path == "/favicon.ico"
        elif "/metrics" in self.path:
            q = parse_qs(urlsplit(self.path).query)
            target = q.get("target")

            if target is None:
                self.send_response(HTTPStatus.BAD_REQUEST)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write("missing target\n\n".encode(self.ENC))
            else:
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/plain;version=0.0.4")
                self.end_headers()
                u = urlparse(url="https://" + target[0], allow_fragments=False)
                client = http.client.HTTPSConnection(u.hostname, u.port, timeout=10)
                success = 0
                try:
                    client.connect()
                    sock = client.sock
                    peer_cert = sock.getpeercert()
                    version = client.sock.version()
                    client.close()
                    #
                    #
                    #
                    success = 1
                    sn = peer_cert["serialNumber"]
                    common_name = self.commonName(peer_cert["subject"])
                    alt_names = self.subjectAlternativeName(peer_cert["subjectAltName"], common_name)
                    not_before = datetime.strptime(peer_cert['notBefore'], "%b %d %X %Y %Z")
                    not_after = datetime.strptime(peer_cert['notAfter'], "%b %d %X %Y %Z")
                    #
                    #
                    #
                    self.wfile.write(h_ssl_tls_version_info)
                    self.wfile.write(t_ssl_tls_version_info)
                    self.wfile.write(bytes(ssl_tls_version_info % version, ENC))
                    self.wfile.write(h_ssl_cert_not_after)
                    self.wfile.write(t_ssl_cert_not_after)
                    self.wfile.write(bytes(ssl_cert_not_after %
                                           (common_name, alt_names, sn, not_after.timestamp()), ENC))
                    self.wfile.write(h_ssl_cert_not_before)
                    self.wfile.write(t_ssl_cert_not_before)
                    self.wfile.write(bytes(ssl_cert_not_before %
                                           (common_name, alt_names, sn, not_before.timestamp()), ENC))

                except BaseException as e:
                    print(e)
                    traceback.print_stack()
                    pass
                # try ... expect
                self.wfile.write(h_ssl_tls_connect_success)
                self.wfile.write(t_ssl_tls_connect_success)
                self.wfile.write(bytes("ssl_tls_connect_success %0.0f\n" % success, ENC))
                self.wfile.write(NL)
            # if target is None
        elif self.path == "/":
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(bytes("<html>\n", ENC))
            self.wfile.write(bytes("\t<body>\n", ENC))
            self.wfile.write(bytes("\t\t<a href='/metrics'>Metrics</a>\n", ENC))
            self.wfile.write(bytes("\t</body>\n", ENC))
            self.wfile.write(bytes("</html>\n", ENC))
        else:
            self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)
            self.end_headers()
        # if self.path
    # do_GET

    def log_message(self, format, *args):
        pass

    def log_error(self):
        pass

    def commonName(self, subject):
        if subject is None:
            return ""
        else:
            tmp = subject
            while isinstance(tmp[0], tuple):
                tmp = tmp[0]
            return tmp[1]
    # def commonName

    def subjectAlternativeName(self, sAN, subject):
        if sAN is None:
            return ""
        else:
            tmp = ""
            for k in sAN:
                if isinstance(k, tuple) and k[0] == "DNS":
                    if k[1] != subject:
                        tmp += "," + k[1]
                # isinstance
            # for k in sAN
            return tmp[1:]
        # sAN is None
    # def subjectAlternativeName
# class
