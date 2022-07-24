from util import long2ip, ip2long
import os


def generate(config, dnat=False):
    public_ip = config["public_ip"]
    current_ip = config["base_ip"]
    hosts = dict()
    for group in config["groups"].values():
        for proxy in group["proxies"]:
            if not dnat:
                add_hosts(hosts, proxy["domain"], public_ip)
            elif not proxy["dnat"]:
                add_hosts(hosts, proxy["domain"], current_ip)
    if dnat:
        for group in config["groups"].values():
            for proxy in group["proxies"]:
                if proxy["dnat"]:
                    current_ip = long2ip(ip2long(current_ip) + 1)
                    add_hosts(hosts, proxy["domain"], current_ip)

    return generate_hosts_content(hosts)


def add_hosts(hosts, domain, current_loopback_ip):
    if(current_loopback_ip in hosts):
        hosts[current_loopback_ip].append(domain)
    else:
        hosts[current_loopback_ip] = [domain]


def generate_hosts_content(hosts):
    result = ''
    for ip, list in hosts.items():
        result += ip + ' ' + " ".join(list) + ' ### GENERATED ' + os.linesep
    return result
