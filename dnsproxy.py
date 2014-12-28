#!/usr/bin/env python

import os
import sys
import argparse
import urllib2
import time
import random
import string

import util

import generators
from generators.util import long2ip, ip2long


def create_pure_sni_config(config, args):

    print_firewall(config)

    print ""

    if "haproxy" not in args.skip_conf:
        haproxy_content = generators.generate_haproxy(config)
        util.put_contents(args.haproxy, haproxy_content, base_dir=args.base_dir)
        print 'File generated: ' + args.haproxy

    if "dnsmasq" not in args.skip_conf:
        dnsmasq_content = generators.generate_dnsmasq(config)
        util.put_contents(args.dnsmasq, dnsmasq_content, base_dir=args.base_dir)
        print 'File generated: ' + args.dnsmasq

    print ""
    print '***********************************************************************************************'
    print 'Caution: it\'s not recommended but it\'s possible to run a (recursive) DNS forwarder on your'
    print 'remote server ' + config["public_ip"] + '. If you leave the DNS port wide open to everyone,'
    print 'your server will get terminated sooner or later because of abuse (DDoS amplification attacks).'
    print '***********************************************************************************************'


def create_non_sni_config(config, args):
    print "Please be aware that this is an advanced option. For most cases, pure-sni will be enough."
    if not config["base_ip"]:
        print "Missing base_ip! Update config.json and re-run the script."
        sys.exit(1)
    if not config["base_port"]:
        print "Missing base_port! Update config.json and re-run the script."
        sys.exit(1)

    current_ip = config["base_ip"]

    print 'Make sure the following IP addresses are available as virtual interfaces on your Ddnsmasq-server:'
    print current_ip
    current_iplong = ip2long(current_ip)
    for group in config["groups"].values():
        for proxy in group["proxies"]:
            if not proxy["catchall"]:
                current_iplong += 1
                print long2ip(current_iplong)

    print_firewall(config, catchall=False)

    print ""
    if "haproxy" not in args.skip_conf:
        haproxy_content = generators.generate_haproxy(config, catchall=False)
        util.put_contents(args.haproxy, haproxy_content, base_dir=args.base_dir)
        print 'File generated: ' + args.haproxy
    if "dnsmasq" not in args.skip_conf:
        dnsmasq_content = generators.generate_dnsmasq(config, catchall=False)
        util.put_contents(args.dnsmasq, dnsmasq_content, base_dir=args.base_dir)
        print 'File generated: ' + args.dnsmasq
    if "iptables" not in args.skip_conf:
        iptables_content = generators.generate_iptables(config)
        util.put_contents(args.iptables, iptables_content, base_dir=args.base_dir)
        print 'File generated: ' + args.iptables


def create_local_non_sni_config(config, args):
    print "Please be aware that this is an advanced option. For most cases, pure-sni will be enough."
    if not config["base_ip"]:
        print "Missing base_ip! Update config.json and re-run the script."
        sys.exit(1)
    if not config["base_port"]:
        print "Missing base_port! Update config.json and re-run the script."
        sys.exit(1)

    print_firewall(config, catchall=False)

    print ""
    if "haproxy" not in args.skip_conf:
        haproxy_content = generators.generate_haproxy(config, catchall=False)
        util.put_contents(args.haproxy, haproxy_content, base_dir=args.base_dir)
        print 'File generated: ' + args.haproxy
    if "hosts" not in args.skip_conf:
        hosts_content = generators.generate_hosts(config)
        util.put_contents(args.hosts, hosts_content, base_dir=args.base_dir)
        print 'File generated: ' + args.hosts
    if "netsh" not in args.skip_conf:
        netsh_content = generators.generate_netsh(config)
        util.put_contents(args.netsh, netsh_content, base_dir=args.base_dir)
        print 'File generated: ' + args.netsh
    if "rinetd" not in args.skip_conf:
        rinetd_content = generators.generate_rinetd(config)
        util.put_contents(args.netsh, rinetd_content, base_dir=args.base_dir)
        print 'File generated: ' + args.netsh


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
    for group in config["groups"].values():
        for proxy in group["proxies"]:
            if not proxy["catchall"]:
                end += len(proxy["protocols"])
    return start, end - 1


def read_config(args):
    if not os.path.isfile("config.json"):
        print "config.json does not exist! Please copy config-sample.json to config.json and edit to your liking, then run the script."
        sys.exit(1)
    if not os.path.isfile("proxies/proxies-%s.json" % args.country.lower()):
        print "The proxy configuration file proxies-%s.json does not exist! Exiting." % args.country.lower()
        sys.exit(1)
    content = util.get_contents("config.json")
    config = util.json_decode(content)
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
        util.put_contents('config.json', util.json_encode(config))

    groups = util.json_decode(util.get_contents("proxies/proxies-%s.json" % args.country.lower()))

    if args.only:
        only = set(args.only)
        for item in args.only:
            if item not in groups:
                print "Nonexistent Item: %s, exiting" % item
                sys.exit()
        for item in groups.keys():
            if item not in only:
                del groups[item]
    elif args.skip:
        for item in args.skip:
            del groups[item]

    config["groups"] = groups

    return config


def main(args):
    config = read_config(args)

    print ""

    # Create the output dir if it doesn't exist
    if not os.path.exists(args.base_dir):
        os.mkdir(args.base_dir)

    if args.mode == "pure-sni":
        create_pure_sni_config(config, args)
    elif args.mode == "non-sni":
        create_non_sni_config(config, args)
    elif args.mode == "local":
        create_local_non_sni_config(config, args)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate configuration files to setup a tunlr style smart DNS")
    parser.add_argument("-m", "--mode", choices=["pure-sni", "non-sni", "local"], default="pure-sni", type=str, help="The mode of configuration files to generate")
    parser.add_argument("-c", "--country", default="us", type=str, help="The country to use for generating the configuration")

    parser.add_argument("--dnsmasq", type=str, default="dnsmasq-haproxy.conf", help="Specify the DNS configuration file name")
    parser.add_argument("--haproxy", type=str, default="haproxy.conf", help="Specify the haproxy configuration file name")
    parser.add_argument("--iptables", type=str, default="iptables-haproxy.sh", help="Specify the iptables configuration file name")
    parser.add_argument("--netsh", type=str, default="netsh-haproxy.cmd", help="Specify the netsh configuration file name")
    parser.add_argument("--hosts", type=str, default="hosts-haproxy.txt", help="Specify the hosts configuration file name")
    parser.add_argument("--rinetd", type=str, default="rinetd-haproxy.conf", help="Specify the rinetd configuration file name")

    parser.add_argument("--ip", type=str, default=None, help="Specify the public ip to use")
    parser.add_argument("--bind-ip", type=str, default=None, help="Specify the ip that haproxy should bind to")
    parser.add_argument("--save", action="store_true", help="Specify wether to save the configuration")
    parser.add_argument("--base-dir", type=str, default="output", help="Specify the output directory")

    parser.add_argument("--skip-conf", default=[], choices=["dnsmasq", "haproxy", "netsh", "hosts", "rinetd"], nargs="*", help="Specify the configuration files to skip generating")
    parser.add_argument("--only", default=None, nargs="*", help="Specify the proxies to use while generating")
    parser.add_argument("--skip", default=None, nargs="*", help="Specify the proxies to not use while generating")

    args = parser.parse_args()
    main(args)
