dnsproxy
========

Project Based on https://github.com/jamiees2/dnsproxy

Added sniproxy and domain list to route specific Domains to the proxy.

Unblock:

Zattoo

Wilmaa

Teleboy

Blue TV (Swisscom)

....and many more.

Prerequisites:
- A VPS based in the country you want, preferrably running Ubuntu 20.04. A 128MB server is enough.
- python
- sniproxy
- dnsmasq


The configuration generator (dnsproxy.py) offers works with sniproxy with the following Setup:
- [sni (Simple Setup)](https://github.com/jamiees2/dnsproxy/wiki/SNI-Setup) (You dont need HAProxy, as we use sniproxy in our project Fork)


You can generate each configuration file separately with `-o`. Example:

```python dnsproxy.py -o sniproxy```

```python dnsproxy.py -o dnsmasq```

Copy and overwrite the generated configs for sniproxy and dnsmasq.
Restart the Service and your dns Proxy should be up and running.

Now just point your DNS Entries to your VPS and the traffic for the needed Domains goes through the Proxy.

It is also possible to specify which proxy list you would like to use, based on country. You can specify that by passing `-c <country>`, where `<country>` is a suffix of any file in the `proxies/` directory. For example, if you wish to generate configuration for a uk based SNI proxy, you can run `python dnsproxy.py -c uk -m sni`. The default country is `ch`.


*If you would like to add a service, please send a pull request.*

Output of `dnsproxy.py -h`:
```
usage: dnsproxy.py [-h] [-m {manual,sni,dnat,local}]
                   [-o {dnsmasq,haproxy,netsh,hosts,rinetd,iptables,iproute2,sniproxy}]
                   [-c COUNTRY [COUNTRY ...]] [-d] [--ip IP]
                   [--bind-ip BIND_IP] [--base-ip BASE_IP]
                   [--base-port BASE_PORT] [--save] [--output-dir OUTPUT_DIR]
                   [--only [ONLY [ONLY ...]]] [--skip [SKIP [SKIP ...]]]
                   [--dnsmasq-filename DNSMASQ_FILENAME]
                   [--haproxy-filename HAPROXY_FILENAME]
                   [--sniproxy-filename SNIPROXY_FILENAME]
                   [--iptables-filename IPTABLES_FILENAME]
                   [--iproute2-filename IPROUTE2_FILENAME]
                   [--netsh-filename NETSH_FILENAME]
                   [--hosts-filename HOSTS_FILENAME]
                   [--rinetd-filename RINETD_FILENAME]

Generate configuration files to setup a tunlr style smart DNS

optional arguments:
  -h, --help            show this help message and exit
  -m {manual,sni,dnat,local}, --mode {manual,sni,dnat,local}
                        Presets for configuration file generation.
  -o {dnsmasq,haproxy,netsh,hosts,rinetd,iptables,iproute2,sniproxy}, --output {dnsmasq,haproxy,netsh,hosts,rinetd,iptables,iproute2,sniproxy}
                        Which configuration file(s) to generate. This is
                        ignored when not in manual mode.
  -c COUNTRY [COUNTRY ...], --country COUNTRY [COUNTRY ...]
                        The country/-ies to use for generating the
                        configuration (space-separated, e.g. -c us uk).
  -d, --dnat            Specify to use DNAT instead of SNI (Advanced). This is
                        ignored when not in manual mode.
  --ip IP               Specify the public IP to use
  --bind-ip BIND_IP     Specify the IP that haproxy should bind to
  --base-ip BASE_IP     Specify the base IP from which DNAT should start
                        generating.
  --base-port BASE_PORT
                        Specify the base port from which DNAT should start
                        generating.
  --save                Specify wether to save the configuration to
                        config.json
  --output-dir OUTPUT_DIR
                        Specify the output directory
  --only [ONLY [ONLY ...]]
                        Specify the proxies to use while generating
  --skip [SKIP [SKIP ...]]
                        Specify the proxies to not use while generating
  --dnsmasq-filename DNSMASQ_FILENAME
                        Specify the DNS configuration file name
  --haproxy-filename HAPROXY_FILENAME
                        Specify the haproxy configuration file name
  --sniproxy-filename SNIPROXY_FILENAME
                        Specify the sniproxy configuration file name
  --iptables-filename IPTABLES_FILENAME
                        Specify the iptables configuration file name
  --iproute2-filename IPROUTE2_FILENAME
                        Specify the iproute2 configuration file name
  --netsh-filename NETSH_FILENAME
                        Specify the netsh configuration file name
  --hosts-filename HOSTS_FILENAME
                        Specify the hosts configuration file name
  --rinetd-filename RINETD_FILENAME
                        Specify the rinetd configuration file name
 ```


