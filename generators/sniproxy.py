from util import fmt, port, chunks
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
    result += fmt('}', indent=None)
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


def generate_dns(dest_addrs):
    if isinstance(dest_addrs, list):
        result = 'address=/' + str(dest_addrs) + '/'
    else:
        result = 'address=/' + dest_addrs + '/'
    return result + os.linesep



def generate_hosts01():
    result = fmt('table hosts{', indent=None)  
    result += os.linesep
    return result 
    
def generate_hosts02(): 
    result = fmt('#    .* *')
    result += fmt('}', indent=None)    
    result += os.linesep
    return result 
  
def generate(config, dnat=False):
    sniproxy_content = ""
    sniproxy_content += generate_startconfig01()
    sniproxy_content += generate_mydns()
    sniproxy_content += generate_error()
    sniproxy_content += generate_listenhttp()
    sniproxy_content += generate_listentls()
    sniproxy_content += generate_hosts01()    

    for group in config["groups"].values():
        c = chunks([proxy["domain"] for proxy in group["proxies"]], 5)

        for chunk in c:
            sniproxy_content += generate_dns(chunk)

    sniproxy_content += generate_hosts02()  





    

    return sniproxy_content