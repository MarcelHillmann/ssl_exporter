import ssl

if __name__ == "__main__":
    for t in ssl.TLSVersion:
        print("1: ", t)

    print(ssl.TLSVersion.MINIMUM_SUPPORTED)
    print(ssl.TLSVersion.MAXIMUM_SUPPORTED)