import os
from util import long2ip, ip2long, port


def generate(config):
    iptables_location = config["iptables_location"]
    public_ip = config["public_ip"]
    current_ip = config["base_ip"]
    current_port = config["base_port"]

    iptables_content = generate_iptables('80', public_ip, current_ip, current_port, iptables_location)
    current_port += 1
    iptables_content += generate_iptables('443', public_ip, current_ip, current_port, iptables_location)
    current_port += 1
    for group in config["groups"].values():
        for proxy in group["proxies"]:
            if proxy["dnat"]:
                current_ip = long2ip(ip2long(current_ip) + 1)
                for protocol in proxy["protocols"]:
                    iptables_content += generate_iptables(port(protocol), public_ip, current_ip, current_port, iptables_location)
                    current_port += 1
    return iptables_content


def generate_iptables(port, public_ip, current_dnat_ip, current_dnat_port, iptables_location):
    result = iptables_location + ' -t nat -A PREROUTING -p tcp --dport ' + str(port) + ' -d ' + current_dnat_ip + ' -j DNAT --to-destination ' + public_ip + ':' + str(current_dnat_port) + os.linesep
    result += iptables_location + ' -t nat -A POSTROUTING -p tcp --dport ' + str(current_dnat_port) + ' -j MASQUERADE' + os.linesep
    return result
