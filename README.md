dnsproxy
========

This is heavily based on @trick77's original work on [tunlr-style-dns-unblocking](https://github.com/trick77/tunlr-style-dns-unblocking/)

Prerequisites:
- python
- haproxy

For `sni` and `dnat` setup:
- dnsmasq


The configuration generator (dnsproxy.py) offers three different possibilities for setup:
- sni (Simple Setup)
- dnat (Advanced Setup)
- local (Advanced Setup)
- manual

See here for additional information: 
- http://trick77.com/2014/03/01/tunlr-style-dns-unblocking-pandora-netflix-hulu-et-al/
- http://trick77.com/2014/03/02/dns-unblocking-using-dnsmasq-haproxy/

*If you would like to add a service, please send a pull request.*

Output of `dnsproxy.py -h`:
```
usage: dnsproxy.py [-h] [-m {manual,sni,dnat,local}]
                   [-o {dnsmasq,haproxy,netsh,hosts,rinetd,iptables} [{dnsmasq,haproxy,netsh,hosts,rinetd,iptables} ...]]
                   [-c COUNTRY] [-d] [--ip IP] [--bind-ip BIND_IP] [--save]
                   [--base-dir BASE_DIR] [--only [ONLY [ONLY ...]]]
                   [--skip [SKIP [SKIP ...]]]
                   [--dnsmasq-filename DNSMASQ_FILENAME]
                   [--haproxy-filename HAPROXY_FILENAME]
                   [--iptables-filename IPTABLES_FILENAME]
                   [--netsh-filename NETSH_FILENAME]
                   [--hosts-filename HOSTS_FILENAME]
                   [--rinetd-filename RINETD_FILENAME]

Generate configuration files to setup a tunlr style smart DNS

optional arguments:
  -h, --help            show this help message and exit
  -m {manual,sni,dnat,local}, --mode {manual,sni,dnat,local}
                        Presets for configuration file generation.
  -o {dnsmasq,haproxy,netsh,hosts,rinetd,iptables} [{dnsmasq,haproxy,netsh,hosts,rinetd,iptables} ...], --output {dnsmasq,haproxy,netsh,hosts,rinetd,iptables} [{dnsmasq,haproxy,netsh,hosts,rinetd,iptables} ...]
                        Which configuration file(s) to generate. This is
                        ignored when not in manual mode.
  -c COUNTRY, --country COUNTRY
                        The country to use for generating the configuration.
  -d, --dnat            Specify to use DNAT instead of SNI (Advanced). This is
                        ignored when not in manual mode.
  --ip IP               Specify the public ip to use
  --bind-ip BIND_IP     Specify the ip that haproxy should bind to
  --save                Specify wether to save the configuration
  --base-dir BASE_DIR   Specify the output directory
  --only [ONLY [ONLY ...]]
                        Specify the proxies to use while generating
  --skip [SKIP [SKIP ...]]
                        Specify the proxies to not use while generating
  --dnsmasq-filename DNSMASQ_FILENAME
                        Specify the DNS configuration file name
  --haproxy-filename HAPROXY_FILENAME
                        Specify the haproxy configuration file name
  --iptables-filename IPTABLES_FILENAME
                        Specify the iptables configuration file name
  --netsh-filename NETSH_FILENAME
                        Specify the netsh configuration file name
  --hosts-filename HOSTS_FILENAME
                        Specify the hosts configuration file name
  --rinetd-filename RINETD_FILENAME
                        Specify the rinetd configuration file name
 ```

You can generate each configuration file separately with `-m manual`. Example:
```python dnsproxy.py -m manual -o haproxy```. `-m manual` is also default, so this can be simplified to ```python dnsproxy.py -o haproxy```.


#### SNI (Simple Setup)

See the Wiki: https://github.com/jamiees2/dnsproxy/wiki/SNI-Setup.
 
#### DNAT (Advanced Setup)

See the Wiki: https://github.com/jamiees2/dnsproxy/wiki/DNAT-Setup.


#### local (Semi-Advanced Setup)

See the Wiki: https://github.com/jamiees2/dnsproxy/wiki/Local-Setup.

