import os
from util import long2ip, ip2long, port


def generate(config):
    public_ip = config["public_ip"]
    current_ip = config["base_ip"]
    current_port = config["base_port"]

    netsh_content = generate_netsh('80', public_ip, current_ip, current_port)
    current_port += 1
    netsh_content += generate_netsh('443', public_ip, current_ip, current_port)
    current_port += 1

    for group in config["groups"].values():
        for proxy in group["proxies"]:
            if not proxy["catchall"]:
                current_ip = long2ip(ip2long(current_ip) + 1)
                for protocol in proxy["protocols"]:
                    netsh_content += generate_netsh(port(protocol), public_ip, current_ip, current_port)
                    current_port += 1
    return netsh_content


def generate_netsh(port, public_ip, current_ip, current_port):
    result = 'netsh interface portproxy add v4tov4 protocol=tcp listenport=' + str(port) + ' listenaddress=' + current_ip + ' connectaddress=' + public_ip + ' connectport=' + str(current_port) + os.linesep
    return result
