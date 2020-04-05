import socketserver
import exporter

if __name__ == "__main__":
    handler = exporter.Exporter
    with socketserver.TCPServer(("", 9000), handler) as httpd:
        print("serving at port 9000")
        httpd.serve_forever()

    print("Server stopped.")
