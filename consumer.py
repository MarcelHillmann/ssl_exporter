from urllib.parse import urlparse
from http.client import HTTPSConnection, BadStatusLine
from datetime import datetime
from os import getenv
import OpenSSL
import ssl


class Consumer:
    __url = None
    __version = ""
    __peer_cert = dict()
    __proto_type = ""

    def __init__(self, target):
        self.__url = urlparse(url="https://" + target[0], allow_fragments=False)

    # def __init__

    def load(self) -> bool:
        try:
            client = self.client_factory()
            client.connect()
            sock = client.sock
            self.__peer_cert = sock.getpeercert()
            self.__version = client.sock.version()
            try:
                client.request("HEAD", "/")
                client.getresponse()
                self.__proto_type = "HTTPS"
            except BaseException as e:
                self.__proto_type = self.__proto(e, "TCP")
                if isinstance(e, SystemExit):
                    raise e
                pass
            client.close()
            return True
        except BaseException as e:
            if isinstance(e, SystemExit):
                raise e
            print(e)
            return False
            # try ... expect
        # def load

    def client_factory(self):
        return HTTPSConnection(self.__url.hostname, self.__url.port, timeout=10)

    def __srvname_callback(self, sslobj, servername, sslctx):
        return True

    def serial_number(self):
        if self.__not_in("subject"):
            return ""

        sn = self.__peer_cert["serialNumber"].lower()
        i, j = 0, 1
        result = ""
        while j < len(sn):
            result += ":%s%s" % (sn[i:(i+1)], sn[j:(j+1)])
            i += 2
            j += 2

        return result[1:]
        # def serial_number

    def version(self):
        return self.__version

    def subject(self):
        if self.__not_in("subject"):
            return ""

        for result in self.__peer_cert["subject"]:
            if result[0][0] == "commonName":
                return result[0][1]
            # subject is None
        # subject

    def __not_in(self, key):
        return key not in self.__peer_cert.keys()
        # __keys

    def alternative_name(self):
        if self.__not_in("subjectAltName"):
            return ""

        subject = self.subject()
        result = ""
        for k in self.__peer_cert["subjectAltName"]:
            if isinstance(k, tuple) and k[0] in ("DNS", "IP Address") and k[1] != subject:
                result += "," + k[1]
                # isinstance and DNS and not subject
            # for k in sAN
        return result[1:]
        # alternative_name

    def not_before(self) -> float:
        if self.__not_in("notBefore"):
            return -1

        return str_to_float(self.__peer_cert['notBefore'])

    # not_before

    def not_after(self) -> float:
        if self.__not_in("notAfter"):
            return -1

        return str_to_float(self.__peer_cert["notAfter"])
        # not_after

    def protocol(self):
        return self.__proto_type

    def __proto(self, e, default):
        if isinstance(e, BadStatusLine):
            bsl = str(e)
            if "SMTP" in bsl:
                return "SMTPS"
            else:
                print(bsl)
                return default
        else:
            return default
    # class Consumer


def str_to_float(value) -> float:
    return datetime.strptime(value, "%b %d %X %Y %Z").timestamp()
    # str_to_float