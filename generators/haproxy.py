from util import fmt, port
import os


def generate(config, dnat=False, test=True):
    bind_ip = config["bind_ip"]
    server_options = config["server_options"]
    if "base_port" in config:
        current_port = config["base_port"]
    elif dnat:
        return

    haproxy_content = generate_global()
    haproxy_content += generate_defaults()

    if not dnat:
        http_port = 80
        https_port = 443
    else:
        http_port = current_port
        https_port = current_port + 1

    haproxy_catchall_frontend_content = generate_frontend('catchall', 'http', bind_ip, http_port, True)
    haproxy_catchall_backend_content = generate_backend('catchall', 'http', None, None, None, True)

    haproxy_catchall_frontend_ssl_content = generate_frontend('catchall', 'https', bind_ip, https_port, True)
    haproxy_catchall_backend_ssl_content = generate_backend('catchall', 'https', None, None, None, True)

    if config["stats"]["enabled"]:
        haproxy_content += generate_stats(config["stats"], bind_ip)

    for group in config["groups"].values():
        for proxy in group["proxies"]:
            if not dnat or (dnat and proxy["dnat"]):
                for protocol in proxy["protocols"]:
                    if protocol == 'http':
                        haproxy_catchall_frontend_content += generate_frontend_catchall_entry(proxy["domain"], protocol)
                        haproxy_catchall_backend_content += generate_backend_catchall_entry(proxy["domain"], protocol, port(protocol), server_options)
                    elif protocol == 'https':
                        haproxy_catchall_frontend_ssl_content += generate_frontend_catchall_entry(proxy["domain"], protocol)
                        haproxy_catchall_backend_ssl_content += generate_backend_catchall_entry(proxy["domain"], protocol, port(protocol), server_options)
    if test:
        haproxy_catchall_frontend_content += generate_frontend_catchall_entry('ptest.verdandi.is', 'http')
        haproxy_catchall_backend_content += generate_backend_catchall_entry('ptest.verdandi.is', 'http', '80', server_options)

        haproxy_catchall_frontend_ssl_content += generate_frontend_catchall_entry('ptest.verdandi.is', 'https')
        haproxy_catchall_backend_ssl_content += generate_backend_catchall_entry('ptest.verdandi.is', 'https', '443', server_options)

    haproxy_content += haproxy_catchall_frontend_content + os.linesep
    haproxy_content += haproxy_catchall_backend_content
    haproxy_content += haproxy_catchall_frontend_ssl_content + os.linesep
    haproxy_content += haproxy_catchall_backend_ssl_content

    if dnat:
        current_port += 2
        for group in config["groups"].values():
            for proxy in group["proxies"]:
                if proxy["dnat"]:
                    for protocol in proxy["protocols"]:
                        haproxy_content += generate_frontend(proxy["alias"], protocol, bind_ip, current_port, False)
                        haproxy_content += generate_backend(proxy["alias"], protocol, proxy["domain"], port(protocol), server_options, False)
                        current_port += 1

    haproxy_content += generate_deadend('http')
    haproxy_content += generate_deadend('https')

    return haproxy_content


def generate_frontend_catchall_entry(domain, mode):
    if mode == 'http':
        return fmt('use_backend b_catchall_' + mode + ' if { hdr_dom(host) -i ' + domain + ' }')
    elif mode == 'https':
        return fmt('use_backend b_catchall_' + mode + ' if { req_ssl_sni -i ' + domain + ' }')

    return None


def generate_backend_catchall_entry(domain, mode, port, server_options, override_domain=None):
    result = None
    if mode == 'http':
        result = fmt('use-server ' + domain + ' if { hdr_dom(host) -i ' + domain + ' }')
        if override_domain is None:
            result += fmt('server ' + domain + ' ' + domain + ':' + str(port) + ' ' + server_options + os.linesep)
        else:
            result += fmt('server ' + domain + ' ' + override_domain + ':' + str(port) + ' ' + server_options + os.linesep)
    elif mode == 'https':
        result = fmt('use-server ' + domain + ' if { req_ssl_sni -i ' + domain + ' }')
        result += fmt('server ' + domain + ' ' + domain + ':' + str(port) + ' ' + server_options + os.linesep)

    return result


def generate_global():
    result = fmt('global', indent=None)
    result += fmt('daemon')
    result += fmt('maxconn 20000')
    result += fmt('user haproxy')
    result += fmt('group haproxy')
    result += fmt('stats socket /var/run/haproxy.sock mode 0600 level admin')
    result += fmt('log /dev/log local0 debug')
    result += fmt('pidfile /var/run/haproxy.pid')
    result += fmt('spread-checks 5')
    result += os.linesep
    return result


def generate_defaults():
    result = fmt('defaults', indent=None)
    result += fmt('maxconn 19500')
    result += fmt('log global')
    result += fmt('mode http')
    result += fmt('option httplog')
    result += fmt('option abortonclose')
    result += fmt('option http-server-close')
    result += fmt('option persist')
    result += fmt('timeout connect 20s')
    result += fmt('timeout client 120s')
    result += fmt('timeout server 120s')
    result += fmt('timeout queue 120s')
    result += fmt('timeout check 10s')
    result += fmt('retries 3')
    result += os.linesep
    return result


def generate_deadend(mode):
    result = fmt('backend b_deadend_' + mode, indent=None)
    if mode == 'http':
        result += fmt('mode http')
        result += fmt('option httplog')
        result += fmt('option accept-invalid-http-response')
        result += fmt('option http-server-close')

    elif mode == 'https':
        result += fmt('mode tcp')
        result += fmt('option tcplog')

    result += os.linesep
    return result


def generate_stats(stats, bind_ip):
    result = fmt('listen stats', indent=None)
    result += fmt('bind ' + bind_ip + ':' + str(stats["port"]))
    result += fmt('mode http')
    result += fmt('stats enable')
    result += fmt('stats realm Protected\\ Area')
    result += fmt('stats uri /')
    result += fmt('stats auth ' + stats["user"] + ':' + stats["password"])
    result += os.linesep
    return result


def generate_frontend(proxy_name, mode, bind_ip, current_port, is_catchall):
    result = fmt('frontend f_' + proxy_name + '_' + mode, indent=None)
    result += fmt('bind ' + bind_ip + ':' + str(current_port))

    if mode == 'http':
        result += fmt('mode http')
        result += fmt('option httplog')
        result += fmt('capture request header Host len 50')
        result += fmt('capture request header User-Agent len 150')

    elif mode == 'https':
        result += fmt('mode tcp')
        result += fmt('option tcplog')
        if is_catchall:
            result += fmt('tcp-request inspect-delay 5s')
            result += fmt('tcp-request content accept if { req_ssl_hello_type 1 }')

    if is_catchall:
        result += fmt('default_backend b_deadend_' + mode)

    else:
        result += fmt('default_backend b_' + proxy_name + '_' + mode)

    result += os.linesep
    return result


def generate_backend(proxy_name, mode, domain, port, server_options, is_catchall):
    result = fmt('backend b_' + proxy_name + '_' + mode, indent=None)

    if mode == 'http':
        result += fmt('mode http')
        result += fmt('option httplog')
        result += fmt('option accept-invalid-http-response')

    elif mode == 'https':
        result += fmt('mode tcp')
        result += fmt('option tcplog')

    if not is_catchall:
        result += fmt('server ' + domain + ' ' + domain + ':' + str(port) + ' ' + server_options)

    return result + os.linesep
