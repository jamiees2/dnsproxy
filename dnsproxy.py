#!/usr/bin/env python

import os
import sys
import argparse
import urllib2
import time
import random
import string
import shutil

import util

import generators
from generators.util import long2ip, ip2long


def print_ips(config):
    current_ip = config["base_ip"]

    print 'Make sure the following IP addresses are available as virtual interfaces on your iptables router:'
    print current_ip
    current_iplong = ip2long(current_ip)
    for group in config["groups"].values():
        for proxy in group["proxies"]:
            if not proxy["dnat"]:
                current_iplong += 1
                print long2ip(current_iplong)


def print_firewall(config, dnat=False):
    bind_ip = config["public_ip"]
    print 'If you are using an inbound firewall on ' + bind_ip + ':'
    if not dnat:
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
            if proxy["dnat"]:
                end += len(proxy["protocols"])
    return start, end - 1


def read_config(args):
    if not os.path.isfile("config.json"):
        print "config.json does not exist! Please copy config-sample.json to config.json and edit to your liking, then run the script."
        sys.exit(1)
    
    countries = args.country
    if isinstance(countries, basestring):
        countries = [countries]
    countries = [country.lower().strip() for country in countries]

    for country in countries:
        if not os.path.isfile("proxies/proxies-%s.json" % country):
            print "The proxy configuration file proxies-%s.json does not exist! Exiting." % country
            sys.exit(1)
    content = util.get_contents("config.json")
    config = util.json_decode(content)
    if args.ip:
        config["public_ip"] = args.ip
    if args.bind_ip:
        config["bind_ip"] = args.ip
    if args.base_ip:
        config["base_ip"] = args.base_ip
    if args.base_port:
        config["base_port"] = args.base_port

    if not config["public_ip"]:
        try:
            print("Autodetecting public IP address...")
            public_ip = urllib2.urlopen("http://curlmyip.com/").read().strip()
            print("Detected public IP as %s. If it's wrong, please cancel the script now and set it in config.json or specify with --ip" % public_ip)
            time.sleep(1)
            config["public_ip"] = public_ip
        except:
            print("Could not detect public IP. Please update the public_ip setting in config.json or specify with --ip.")
            sys.exit(1)

    if args.save:
        util.put_contents('config.json', util.json_encode(config))

    groups = {}
    for country in countries:
        groups.update(util.json_decode(util.get_contents("proxies/proxies-%s.json" % country)))

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

    # Empty the output directory
    shutil.rmtree(args.output_dir, ignore_errors=True)
    # Create the output dir if it doesn't exist
    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)

    # Choose from the available modes
    if args.mode == "sni":
        files = ["haproxy", "dnsmasq", "hosts"]
        dnat = False
    elif args.mode == "dnat":
        files = ["haproxy", "dnsmasq", "hosts", "iptables"]
        dnat = True
    elif args.mode == "local":
        files = ["haproxy", "hosts", "rinetd", "netsh"]
        dnat = True
    else:
        files = args.output
        dnat = args.dnat
        # Work around an argparse bug that appends to the default list rather
        # than replace it.
        if len(files) > 1:
            files = files[1:]

    # Set dnat specific options, make sure required configuration is present
    if dnat:
        print "Please be aware that this is an advanced option. For most cases, pure-sni will be enough."
        if not config["base_ip"]:
            print "Missing base_ip! Update config.json and re-run the script."
            sys.exit(1)
        if not config["base_port"]:
            print "Missing base_port! Update config.json and re-run the script."
            sys.exit(1)
        dnat = True
        print_ips(config)

    for output in set(files):
        if output == "haproxy":
            print_firewall(config, dnat=dnat)
            if config["stats"]["enabled"] and not config["stats"]["password"]:
                print ""
                print "Missing haproxy stats password! Autogenerating one..."
                config["stats"]["password"] = ''.join(random.choice(string.ascii_letters + string.digits) for _ in xrange(10))
                print("HAProxy stats password is %s, please make a note of it." % config["stats"]["password"])
            print ""
            haproxy_content = generators.generate_haproxy(config, dnat=dnat, test=args.test)
            util.put_contents(args.haproxy_filename, haproxy_content, base_dir=args.output_dir)
            print 'File generated: ' + args.haproxy_filename
        elif output == "dnsmasq":
            print ""
            print '***********************************************************************************************'
            print 'Caution: It\'s possible to run a (recursive) DNS forwarder on your remote server ' + config["public_ip"] + '.'
            print 'If you leave the DNS port wide open to everyone, your server will most likely get terminated'
            print 'sooner or later because of abuse (DDoS amplification attacks).'
            print '***********************************************************************************************'
            print ""

            dnsmasq_content = generators.generate_dnsmasq(config, dnat=dnat, test=args.test)
            util.put_contents(args.dnsmasq_filename, dnsmasq_content, base_dir=args.output_dir)
            print 'File generated: ' + args.dnsmasq_filename
        elif output == "hosts":
            hosts_content = generators.generate_hosts(config, dnat=dnat, test=args.test)
            util.put_contents(args.hosts_filename, hosts_content, base_dir=args.output_dir)
            print 'File generated: ' + args.hosts_filename
        elif not dnat:
            print "Output %s cannot be generated" % output
            continue
        elif output == "iptables":
            iptables_content = generators.generate_iptables(config)
            util.put_contents(args.iptables_filename, iptables_content, base_dir=args.output_dir)
            print 'File generated: ' + args.iptables_filename
        elif output == "netsh":
            netsh_content = generators.generate_netsh(config)
            util.put_contents(args.netsh_filename, netsh_content, base_dir=args.output_dir)
            print 'File generated: ' + args.netsh_filename
        elif output == "rinetd":
            rinetd_content = generators.generate_rinetd(config)
            util.put_contents(args.rinetd_filename, rinetd_content, base_dir=args.output_dir)
            print 'File generated: ' + args.rinetd_filename
        else:
            print "Output %s cannot be generated" % output

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate configuration files to setup a tunlr style smart DNS")

    parser.add_argument("-m", "--mode", choices=["manual", "sni", "dnat", "local"], default="manual", type=str, help="Presets for configuration file generation.")
    parser.add_argument("-o", "--output", choices=["dnsmasq", "haproxy", "netsh", "hosts", "rinetd", "iptables"], default=["haproxy"], action="append", help="Which configuration file(s) to generate. This is ignored when not in manual mode.")
    parser.add_argument("-c", "--country", default="us", type=str, nargs="+", help="The country/-ies to use for generating the configuration (space-separated, e.g. -c us uk).")
    parser.add_argument("-d", "--dnat", action="store_true", help="Specify to use DNAT instead of SNI (Advanced). This is ignored when not in manual mode.")
    parser.add_argument("--no-test", dest="test", action="store_false", help="Specify to skip generating test configuration. This means that you will not be able to test your setup with the setup tester.")

    parser.add_argument("--ip", type=str, default=None, help="Specify the public IP to use")
    parser.add_argument("--bind-ip", type=str, default=None, help="Specify the IP that haproxy should bind to")
    parser.add_argument("--base-ip", type=str, default=None, help="Specify the base IP from which DNAT should start generating.")
    parser.add_argument("--base-port", type=str, default=None, help="Specify the base port from which DNAT should start generating.")

    parser.add_argument("--save", action="store_true", help="Specify wether to save the configuration to config.json")
    parser.add_argument("--output-dir", type=str, default="output", help="Specify the output directory")

    parser.add_argument("--only", default=None, nargs="*", help="Specify the proxies to use while generating")
    parser.add_argument("--skip", default=None, nargs="*", help="Specify the proxies to not use while generating")

    parser.add_argument("--dnsmasq-filename", type=str, default="dnsmasq-haproxy.conf", help="Specify the DNS configuration file name")
    parser.add_argument("--haproxy-filename", type=str, default="haproxy.conf", help="Specify the haproxy configuration file name")
    parser.add_argument("--iptables-filename", type=str, default="iptables-haproxy.sh", help="Specify the iptables configuration file name")
    parser.add_argument("--netsh-filename", type=str, default="netsh-haproxy.cmd", help="Specify the netsh configuration file name")
    parser.add_argument("--hosts-filename", type=str, default="hosts-haproxy.txt", help="Specify the hosts configuration file name")
    parser.add_argument("--rinetd-filename", type=str, default="rinetd-haproxy.conf", help="Specify the rinetd configuration file name")

    args = parser.parse_args()
    main(args)
