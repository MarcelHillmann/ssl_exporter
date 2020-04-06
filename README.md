# SSL Exporter

## synopsis

## functions

## samples
```text
# HELP ssl_tls_version_info The TLS version used
# TYPE ssl_tls_version_info gauge
ssl_tls_version_info{version="TLSv1.2"} 1
ssl_tls_version_info{version="HTTPS"} 1
# HELP ssl_cert_not_after NotAfter expressed as a Unix Epoch Time
# TYPE ssl_cert_not_after gauge
ssl_cert_not_after{cn="www.google.com",dnsnames="*.google.com",sn=\"00:00:00:00:00:00:00:00\"} 1586502000
# HELP ssl_cert_not_before NotBefore expressed as a Unix Epoch Time
# TYPE ssl_cert_not_before gauge
ssl_cert_not_before{cn="www.google.com",dnsnames="*.google.com",sn=\"00:00:00:00:00:00:00:00\"} 1585897200
# HELP t_ssl_tls_connect_success connect successfully
# TYPE t_ssl_tls_connect_success gauge
ssl_tls_connect_success 1
```