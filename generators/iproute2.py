import os
from util import long2ip, ip2long


def generate(config):
    current_ip = config["base_ip"]
    local_subnet = config["local_subnet"]
    local_device = config["local_device"]

    iproute2_content = generate_iproute2(current_ip, local_subnet, local_device)
    for group in config["groups"].values():
        for proxy in group["proxies"]:
            if proxy["dnat"]:
                current_ip = long2ip(ip2long(current_ip) + 1)
                iproute2_content += generate_iproute2(current_ip, local_subnet, local_device)
    return iproute2_content


def generate_iproute2(current_dnat_ip, subnet, device):
    result = 'ip addr add ' + current_dnat_ip + '/' + str(subnet) + ' dev ' + device + os.linesep
    return result