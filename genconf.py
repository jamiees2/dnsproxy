#!/usr/bin/env python

import os
import sys
import argparse
import urllib2
import time
from random import SystemRandom
import string

from util import *

from generators import *
from generators.util import *

BASE_DIR = "generated"
random = SystemRandom()


def create_pure_sni_config(config, haproxy_out_filename=None, dnsmasq_out_filename=None):

    dnsmasq_content = generate_dnsmasq(config)
    haproxy_content = generate_haproxy(config)

    print_firewall(config)

    print ""
    if haproxy_out_filename is not None:
        put_contents(haproxy_out_filename, haproxy_content, base_dir=BASE_DIR)
        print 'File generated: ' + haproxy_out_filename

    if dnsmasq_out_filename is not None:
        put_contents(dnsmasq_out_filename, dnsmasq_content, base_dir=BASE_DIR)
        print 'File generated: ' + dnsmasq_out_filename

    print ""
    print '***********************************************************************************************'
    print 'Caution: it\'s not recommended but it\'s possible to run a (recursive) DNS forwarder on your'
    print 'remote server ' + config["public_ip"] + '. If you leave the DNS port wide open to everyone,'
    print 'your server will get terminated sooner or later because of abuse (DDoS amplification attacks).'
    print '***********************************************************************************************'


def create_non_sni_config(config, haproxy_out_filename=None, dnsmasq_out_filename=None, iptables_out_filename=None):
    print "Please be aware that this is an advanced option. For most cases, pure-sni will be enough."
    if not config["base_ip"]:
        print "Missing base_ip! Update config.json and re-run the script."
        sys.exit(1)

    current_ip = config["base_ip"]

    print 'Make sure the following IP addresses are available as virtual interfaces on your Ddnsmasq-server:'
    print current_ip
    current_iplong = ip2long(current_ip)
    for proxy in config["proxies"]:
        if proxy["enabled"] and not proxy["catchall"]:
            current_iplong += 1
            print long2ip(current_iplong)

    print_firewall(config, catchall=False)

    print ""
    if haproxy_out_filename is not None:
        haproxy_content = generate_haproxy(config, catchall=False)
        put_contents(haproxy_out_filename, haproxy_content, base_dir=BASE_DIR)
        print 'File generated: ' + haproxy_out_filename
    if dnsmasq_out_filename is not None:
        dnsmasq_content = generate_dnsmasq(config, catchall=False)
        put_contents(dnsmasq_out_filename, dnsmasq_content, base_dir=BASE_DIR)
        print 'File generated: ' + dnsmasq_out_filename
    if iptables_out_filename is not None:
        iptables_content = generate_iptables(config)
        put_contents(iptables_out_filename, iptables_content, base_dir=BASE_DIR)
        print 'File generated: ' + iptables_out_filename


def create_local_non_sni_config(config, haproxy_out_filename=None, netsh_out_filename=None, hosts_out_filename=None, rinetd_out_filename=None):
    print "Please be aware that this is an advanced option. For most cases, pure-sni will be enough."
    if not config["base_ip"]:
        print "Missing base_ip! Update config.json and re-run the script."
        sys.exit(1)

    print_firewall(config, catchall=False)

    print ""
    if haproxy_out_filename is not None:
        haproxy_content = generate_haproxy(config, catchall=False)
        put_contents(haproxy_out_filename, haproxy_content, base_dir=BASE_DIR)
        print 'File generated: ' + haproxy_out_filename
    if hosts_out_filename is not None:
        hosts_content = generate_hosts(config)
        put_contents(hosts_out_filename, hosts_content, base_dir=BASE_DIR)
        print 'File generated: ' + hosts_out_filename
    if netsh_out_filename is not None:
        netsh_content = generate_netsh(config)
        put_contents(netsh_out_filename, netsh_content, base_dir=BASE_DIR)
        print 'File generated: ' + netsh_out_filename
    if rinetd_out_filename is not None:
        rinetd_content = generate_rinetd(config)
        put_contents(rinetd_out_filename, rinetd_content, base_dir=BASE_DIR)
        print 'File generated: ' + rinetd_out_filename


def print_firewall(config, catchall=True):
    bind_ip = config["public_ip"]
    print 'If you are using an inbound firewall on ' + bind_ip + ':'
    if catchall:
        if config["stats"]["enabled"]:
            print config["iptables_location"] + ' -A INPUT -p tcp -m state --state NEW -d ' + bind_ip + ' --dport ' + str(config["stats"]["port"]) + ' -j ACCEPT'

        print config["iptables_location"] + ' -A INPUT -p tcp -m state --state NEW -m multiport -d ' + bind_ip + ' --dports ' + "80" + ',' + "443" + ' -j ACCEPT'
    else:
        if config["stats"]["enabled"]:
            print config["iptables_location"] + ' -A INPUT -p tcp -m state --state NEW -d ' + bind_ip + ' --dport ' + str(config["stats"]["port"]) + ' -j ACCEPT'

        print config["iptables_location"] + ' -A INPUT -p tcp -m state --state NEW -m multiport -d ' + bind_ip + ' --dports ' + str(config["base_port"]) + ':' + str(port_range(config)) + ' -j ACCEPT'


def port_range(config):
    start = config["base_port"]
    end = start + 2
    for proxy in config["proxies"]:
        if proxy["enabled"] and not proxy["catchall"]:
            end += len(proxy["modes"])
    return start, end - 1


def read_config(args):
    if not os.path.isfile("config.json"):
        print "config.json does not exist! Please copy config-sample.json to config.json and edit to your liking, then run the script."
        sys.exit(1)
    content = get_contents("config.json")
    config = json_decode(content)
    if args.ip:
        config["public_ip"] = args.ip
    if args.bind_ip:
        config["bind_ip"] = args.ip

    if not config["public_ip"]:
        try:
            print("Autodetecting public IP address...")
            public_ip = urllib2.urlopen("http://curlmyip.com/").read().strip()
            print("Detected public IP as %s. If it's wrong, please cancel the script now and set it in config.json" % public_ip)
            time.sleep(1)
            config["public_ip"] = public_ip
        except:
            print("Could not detect public IP. Please change the public_ip setting in config.json before building.")
            sys.exit(1)
    if config["stats"]["enabled"] and not config["stats"]["password"]:
        print "Missing haproxy stats password! Autogenerating one..."
        config["stats"]["password"] = ''.join(random.choice(string.ascii_letters + string.digits) for _ in xrange(10))
        print("HAProxy stats password is %s, please make a note of it." % config["stats"]["password"])

    if args.save:
        put_contents('config.json', json_encode(config))

    proxies = json_decode(get_contents("proxies.json"))
    config["proxies"] = proxies

    return config


def main(args):
    config = read_config(args)

    print ""

    # Create the output dir if it doesn't exist
    if not os.path.exists(BASE_DIR):
        os.mkdir(BASE_DIR)

    if args.cmd == "pure-sni":
        create_pure_sni_config(config, args.haproxy, args.dnsmasq)
    elif args.cmd == "non-sni":
        create_non_sni_config(config, args.haproxy, args.dnsmasq, args.iptables)
    elif args.cmd == "local":
        create_local_non_sni_config(config, args.haproxy, args.netsh, args.hosts, args.rinetd)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate configuration files to setup a tunlr style smart DNS")
    parser.add_argument("cmd", choices=["pure-sni", "non-sni", "local"], nargs="?", default="pure-sni", type=str, help="The mode of configuration files to generate")

    parser.add_argument("--dnsmasq", type=str, default="dnsmasq-haproxy.conf", const=None, nargs="?", help="Specify the DNS configuration file name (leave blank to skip)")
    parser.add_argument("--haproxy", type=str, default="haproxy.conf", const=None, nargs="?", help="Specify the haproxy configuration file name (leave blank to skip)")
    parser.add_argument("--iptables", type=str, default="iptables-haproxy.sh", const=None, nargs="?", help="Specify the iptables configuration file name (leave blank to skip)")
    parser.add_argument("--netsh", type=str, default="netsh-haproxy.cmd", const=None, nargs="?", help="Specify the netsh configuration file name (leave blank to skip)")
    parser.add_argument("--hosts", type=str, default="hosts-haproxy.txt", const=None, nargs="?", help="Specify the hosts configuration file name (leave blank to skip)")
    parser.add_argument("--rinetd", type=str, default="rinetd-haproxy.conf", const=None, nargs="?", help="Specify the rinetd configuration file name (leave blank to skip)")

    parser.add_argument("--ip", type=str, default=None, help="Specify the public ip to use")
    parser.add_argument("--bind-ip", type=str, default=None, help="Specify the ip that haproxy should bind to")
    parser.add_argument("--save", action="store_true", help="Specify wether to save the configuration.")

    args = parser.parse_args()
    main(args)
