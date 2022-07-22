from util import fmt, port
import os

def generate_startconfig01():
    result = fmt('# sniproxy example configuration file', indent=None)
    result += fmt('# lines that start with # are comments', indent=None)
    result += fmt('# lines with only white space are ignored', indent=None)
    result += fmt('', indent=None)
    result += fmt('user daemon', indent=None)
    result += fmt('', indent=None)    
    result += fmt('# PID file', indent=None)
    result += fmt('pidfile /var/run/sniproxy.pid', indent=None)  
    result += os.linesep
    return result

def generate_mydns():
    result = fmt('resolver {', indent=None)
    result += fmt('nameserver 8.8.8.8')
    result += fmt('nameserver 8.8.4.4')
    result += fmt('mode ipv4_only')
    result = fmt('}', indent=None)
    result += os.linesep
    return result

def generate_error():
    result = fmt('error_log {', indent=None)
    result += fmt('# Log to the daemon syslog facility')
    result += fmt('syslog daemon')
    result += fmt('', indent=None)
    result += fmt('# Alternatively we could log to file')
    result += fmt('#filename /var/log/sniproxy/sniproxy.log')
    result += fmt('', indent=None)    
    result += fmt('# Control the verbosity of the log')
    result += fmt('priority notice')
    result += fmt('}', indent=None)     
    result += os.linesep
    return result
 
def generate_listenhttp():
    result = fmt('# blocks are delimited with {...}', indent=None)
    result += fmt('listen 80 {', indent=None)
    result += fmt('proto http')
    result += fmt('table hosts')
    result += fmt('# Fallback backend server to use if we can not parse the client request')
    result += fmt('fallback localhost:8080')
    result += fmt('', indent=None)    
    result += fmt('access_log {')
    result += fmt('filename /var/log/sniproxy/http_access.log')
    result += fmt('priority notice')
    result += fmt('}')
    result += fmt('}', indent=None)    
    result += os.linesep
    return result

def generate_listentls():
    result = fmt('# blocks are delimited with {...}', indent=None)
    result += fmt('listen 443 {', indent=None)
    result += fmt('proto tls')
    result += fmt('table hosts')
    result += fmt('', indent=None)    
    result += fmt('access_log {')
    result += fmt('filename /var/log/sniproxy/https_access.log')
    result += fmt('priority notice')
    result += fmt('}')
    result += fmt('}', indent=None)    
    result += os.linesep
    return result 

def generate_hosts():
    result = fmt('table hosts{', indent=None)
    result += fmt('.*\.wieistmeineip\.de$ *')
    result += fmt('.*\.speedtest\.net$ *')
    result += fmt('wieistmeineip.de wieistmeineip.de')
    result += fmt('speedtest.net speedtest.net')    
    result += fmt('#    .* *')
    result += fmt('}', indent=None)    
    result += os.linesep
    return result 
  
def generate(config, dnat=False):
    bind_ip = config["bind_ip"]
    server_options = config["server_options"]

    sniproxy_content = generate_startconfig01()
    sniproxy_content += generate_mydns()
    sniproxy_content += generate_error()
    sniproxy_content += generate_listenhttp()
    sniproxy_content += generate_listentls()
    sniproxy_content += generate_hosts()
    #sniproxy_content += generate_global()
    #sniproxy_content += generate_defaults()

    http_port = 80
    https_port = 443

    sniproxy_catchall_frontend_content = generate_frontend('catchall', 'http', bind_ip, http_port, True)
    sniproxy_catchall_backend_content = generate_backend('catchall', 'http', None, None, None, True)

    sniproxy_catchall_frontend_ssl_content = generate_frontend('catchall', 'https', bind_ip, https_port, True)
    sniproxy_catchall_backend_ssl_content = generate_backend('catchall', 'https', None, None, None, True)

    for group in config["groups"].values():
        for proxy in group["proxies"]:
            if not dnat or (dnat and not proxy["dnat"]):
                for protocol in proxy["protocols"]:
                    if protocol == 'http':
                        sniproxy_catchall_frontend_content += generate_frontend_catchall_entry(proxy["domain"], protocol)
                        sniproxy_catchall_backend_content += generate_backend_catchall_entry(proxy["domain"], protocol, port(protocol), server_options)
                    elif protocol == 'https':
                        sniproxy_catchall_frontend_ssl_content += generate_frontend_catchall_entry(proxy["domain"], protocol)
                        sniproxy_catchall_backend_ssl_content += generate_backend_catchall_entry(proxy["domain"], protocol, port(protocol), server_options)

    sniproxy_content += sniproxy_catchall_frontend_content + os.linesep
    sniproxy_content += sniproxy_catchall_backend_content
    sniproxy_content += sniproxy_catchall_frontend_ssl_content + os.linesep
    sniproxy_content += sniproxy_catchall_backend_ssl_content

    if dnat:
        current_port += 2
        for group in config["groups"].values():
            for proxy in group["proxies"]:
                if proxy["dnat"]:
                    for protocol in proxy["protocols"]:
                        sniproxy_content += generate_frontend(proxy["alias"], protocol, bind_ip, current_port, False)
                        sniproxy_content += generate_backend(proxy["alias"], protocol, proxy["domain"], port(protocol), server_options, False)
                        current_port += 1

    sniproxy_content += generate_deadend('http')
    sniproxy_content += generate_deadend('https')

    return sniproxy_content