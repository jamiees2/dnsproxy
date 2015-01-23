from util import long2ip, ip2long, chunks
import os


def generate(config, dnat=False, test=True):
    public_ip = config["public_ip"]
    current_ip = config["base_ip"]
    dnsmasq_content = ""
    for group in config["groups"].values():
        if not dnat:
            c = chunks([proxy["domain"] for proxy in group["proxies"]], 5)
        else:
            c = chunks([proxy["domain"] for proxy in group["proxies"] if proxy["dnat"]], 5)

        for chunk in c:
            if not dnat:
                dnsmasq_content += generate_dns(chunk, public_ip)
            else:
                dnsmasq_content += generate_dns(chunk, current_ip)

    if test:
        if not dnat:
            dnsmasq_content += generate_dns('ptest.verdandi.is', public_ip)
            dnsmasq_content += generate_dns('ptest2.verdandi.is', public_ip)
        else:
            dnsmasq_content += generate_dns('ptest.verdandi.is', current_ip)
            dnsmasq_content += generate_dns('ptest2.verdandi.is', current_ip)

    if dnat:
        for group in config["groups"].values():
            for proxy in group["proxies"]:
                if not proxy["dnat"]:
                    current_ip = long2ip(ip2long(current_ip) + 1)
                    dnsmasq_content += generate_dns(proxy["domain"], current_ip)

    return dnsmasq_content


def generate_dns(dest_addrs, current_ip):
    if isinstance(dest_addrs, list):
        result = 'address=/' + "/".join(dest_addrs) + '/' + current_ip
    else:
        result = 'address=/' + dest_addrs + '/' + current_ip
    return result + os.linesep
