import ssl
import unittest
from datetime import datetime
from http.client import HTTPSConnection
from http.server import HTTPServer, SimpleHTTPRequestHandler
from unittest.mock import MagicMock
from consumer import Consumer
from OpenSSL import crypto
from os import remove
from threading import Thread


class TestCaseConsumer(unittest.TestCase):

    @classmethod
    def tearDownClass(cls):
        remove("./unittest.crt")
        remove("./unittest.key")
        # tearDownClass

    def test_SAN(self):
        ts = generator(cn="foo.bar.local")
        with server(ssl.PROTOCOL_TLSv1_2) as s:
            consumer = self.__consumer()
            self.assertTrue(consumer.load())
            self.assertEqual("TLSv1.2", consumer.version(), "version")
            self.assertEqual("HTTPS", consumer.protocol(), "protocol")
            self.assertEqual("foo.bar.local", consumer.subject(), "subject")
            self.assertEqual("03:e8", consumer.serial_number(), "sn")
            self.assertEqual("localhost,127.0.0.1", consumer.alternative_name(), "sAN")
            self.assertEqual(ts["after"], consumer.not_after(), "after")
            self.assertEqual(ts["before"], consumer.not_before(), "before")
            # with server
        # test_SAN

    def test_TLSv1_0(self):
        ts = generator(cn="foo.bar.local", san=False)
        with server(ssl.PROTOCOL_TLSv1) as s:
            consumer = self.__consumer()
            self.assertTrue(consumer.load())
            self.assertEqual("TLSv1", consumer.version(), "version")
            self.assertEqual("foo.bar.local", consumer.subject(), "subject")
            self.assertEqual("03:e8", consumer.serial_number(), "sn")
            self.assertEqual("", consumer.alternative_name(), "sAN")
            self.assertEqual(ts["after"], consumer.not_after(), "after")
            self.assertEqual(ts["before"], consumer.not_before(), "before")
            # with server
        # test_TLSv1_0

    def test_TLSv1_1(self):
        ts = generator()
        with server(ssl.PROTOCOL_TLSv1_1) as s:
            consumer = self.__consumer()
            self.assertTrue(consumer.load())
            self.assertEqual("TLSv1.1", consumer.version(), "version")
            self.assertEqual("localhost", consumer.subject(), "subject")
            self.assertEqual("03:e8", consumer.serial_number(), "sn")
            self.assertEqual("127.0.0.1", consumer.alternative_name(), "sAN")
            self.assertEqual(ts["after"], consumer.not_after(), "after")
            self.assertEqual(ts["before"], consumer.not_before(), "before")
            # with server
        # test_TLSv1_1

    def test_TLSv1_2(self):
        ts = generator()
        with server(ssl.PROTOCOL_TLSv1_2) as s:
            consumer = self.__consumer()
            self.assertTrue(consumer.load())
            self.assertEqual("TLSv1.2", consumer.version(), "version")
            self.assertEqual("localhost", consumer.subject(), "subject")
            self.assertEqual("03:e8", consumer.serial_number(), "sn")
            self.assertEqual("127.0.0.1", consumer.alternative_name(), "sAN")
            self.assertEqual(ts["after"], consumer.not_after(), "after")
            self.assertEqual(ts["before"], consumer.not_before(), "before")
            # with server
        # test_TLSv1_2

    def test_no_subject(self):
        generator(no_subject=True)
        with server(ssl.PROTOCOL_TLSv1_2) as s:
            consumer = self.__consumer()
            self.assertFalse(consumer.load())
            self.assertEqual("", consumer.version(), "version")
            self.assertEqual("", consumer.subject(), "subject")
            self.assertEqual("", consumer.serial_number(), "sn")
            self.assertEqual("", consumer.alternative_name(), "sAN")
            self.assertEqual(-1, consumer.not_after(), "after")
            self.assertEqual(-1, consumer.not_before(), "before")
            # with server
        # test_TLSv1_2

    def __consumer(self) -> Consumer:
        consumer = Consumer(('localhost:50510',))
        consumer.client_factory = client_factory()
        return consumer
    # class


def client_factory():
    ctx = ssl.create_default_context(cafile="./unittest.crt")
    ctx.check_hostname = False
    return MagicMock(return_value=HTTPSConnection(host="localhost", port=50510, timeout=10, context=ctx))
    # client_factory


def generator(cn: str = "localhost", san: bool = True, no_subject: bool = False):
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 3072)

    cert = crypto.X509()
    if not no_subject:
        subject = cert.get_subject()
        subject.C, subject.ST, subject.L, subject.O, subject.OU, subject.CN = "DE", "Bavaria", "Munich", "unit", "test", cn

    issuer = cert.get_issuer()
    issuer.C, issuer.ST, issuer.L, issuer.O, issuer.OU, issuer.CN = "DE", "Bavaria", "Munich", "unit", "test", cn

    if san:
        cert.add_extensions(extensions=[crypto.X509Extension("subjectAltName".encode("utf-8"),
                                                             False,
                                                             "DNS:localhost, IP:127.0.0.1".encode("utf-8"))])
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(-10)
    cert.gmtime_adj_notAfter(3600)
    cert.set_pubkey(key)
    cert.sign(key, "sha1")

    with open("./unittest.crt", "w") as c, \
            open("./unittest.key", "w") as k:
        c.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode("utf-8"))
        k.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key).decode("utf-8"))
    return {"before": ssl.cert_time_to_seconds(cert.get_notBefore().decode("utf-8")),
            "after": ssl.cert_time_to_seconds(cert.get_notAfter().decode("utf-8"))}
    # generator


def server(ssl_version):
    class TestServer(HTTPServer):

        def __init__(self, handlerClass):
            HTTPServer.__init__(self, ('127.0.0.1', 50510), handlerClass, True)
            # __init__

        def get_request(self):
            newsocket, fromaddr = self.socket.accept()
            stream = ssl.wrap_socket(newsocket, server_side=True, certfile="./unittest.crt", keyfile="./unittest.key",
                                     ssl_version=ssl_version)
            return stream, fromaddr
            # get_request
        # TestServer

    class testHandler(SimpleHTTPRequestHandler):

        def log_request(self, code='-', size='-'): pass

        def log_error(self, format, *args): pass

        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(bytes(""))
        # testHandler

    class server(object):

        def __init__(self):
            self.srv = TestServer(testHandler)
            # __init__

        def __enter__(self):
            self.thread = Thread(target=self.srv.serve_forever)
            self.thread.start()
            # __enter__

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.srv.shutdown()
            self.srv.server_close()
            self.thread.join()

        # class server

    return server()
    # server


if __name__ == '__main__':
    unittest.main(failfast=True, buffer=False, catchbreak=False)
    # __name___ == __main__


"""
    @unittest.skip("not fully implemented")
    def test_Non_Https(self):
        consumer = self.__consumer()
        self.assertTrue(consumer.load())
        self.assertEqual("TLSv1.3", consumer.version(), "version")
        self.assertEqual("TCP", consumer.protocol(), "protocol")
        self.assertEqual("localhost", consumer.subject(), "subject")
        self.assertEqual("03:e8", consumer.serial_number(), "sn")
        self.assertEqual("127.0.0.1", consumer.alternative_name(), "sAN")


    """