dnsproxy
========

This is heavily based on @trick77's original work on [tunlr-style-dns-unblocking](https://github.com/trick77/tunlr-style-dns-unblocking/)

Prerequisites:
- python
- haproxy

For `pure-sni` and `non-sni` setup:
- dnsmasq


The configuration generator (dnsproxy.py) offers three different possibilities for setup:
- pure-sni (Simple Setup)
- non-sni (Advanced Setup)
- local (Advanced Setup)

See here for additional information: 
- http://trick77.com/2014/03/01/tunlr-style-dns-unblocking-pandora-netflix-hulu-et-al/
- http://trick77.com/2014/03/02/dns-unblocking-using-dnsmasq-haproxy/

If you would like to add a service, please send a pull request.

Usage: 
```
dnsproxy.py [-h] [-m {manual,pure-sni,non-sni,local}]
                   [-o {dnsmasq,haproxy,netsh,hosts,rinetd,iptables} [{dnsmasq,haproxy,netsh,hosts,rinetd,iptables} ...]]
                   [-c COUNTRY] [-n] [--ip IP] [--bind-ip BIND_IP] [--save]
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
  -m {manual,pure-sni,non-sni,local}, --mode {manual,pure-sni,non-sni,local}
                        Which mode to use when generating configuration files.
  -o {dnsmasq,haproxy,netsh,hosts,rinetd,iptables} [{dnsmasq,haproxy,netsh,hosts,rinetd,iptables} ...], --conf {dnsmasq,haproxy,netsh,hosts,rinetd,iptables} [{dnsmasq,haproxy,netsh,hosts,rinetd,iptables} ...]
                        Which configuration file(s) to generate. This is
                        ignored when not in manual mode.
  -c COUNTRY, --country COUNTRY
                        The country to use for generating the configuration.
  -n, --catchall        Specify to generate configuration for a non-sni based
                        setup. This is ignored when not in manual mode.
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
```python dnsproxy.py -m manual -o haproxy```


#### pure-sni (Simple Setup)

Use this setup if all your multimedia players are SNI-capable. (This is usually the case.)

Requires a U.S. based server (a 128 MB low end VPS is enough) and preferrably a local Dnsmasq DNS forwarder. DD-WRT routers or a Raspberry Pi will do. You can run Dnsmasq on the remote server as well but please be aware of the security and latency issues.

In pure-sni mode, you don't have to worry about the `base_ip` and the `base_port` options. Those options are not used, just leave them at their defaults. Make sure `iptables_location` points to the iptables executable and enter your VPS' IP address in `public_ip`. Make sure the ports 80 and 443 on your VPS are not being used by some other software like Apache2. Use ```netstat -tulpn``` to make sure.

For this mode, call the generator like this:
```python dnsproxy.py -m pure-sni```

The generator will create these two files:
- output/haproxy.conf
- output/dnsmasq-haproxy.conf
 
#### non-sni (Advanced Setup)

non-sni mode enables DNS-unblocking for multimedia players (or applications) which can't handle SNI but still using just a single IP address using some netfilter trickery. See [here](http://trick77.com/2014/04/02/netflix-dns-unblocking-without-sni-xbox-360-ps3-samsung-tv/) for more information on this mode:

Test your new setup with http://trick77.com/dns-unblocking-setup-tester/

Non-conclusive list of devices which don't understand SNI:
- Xbox 360 
- PS3
- All Sony Bravia TVs and Blu-ray players 
- Older Samsung TVs

Use the generator as follows:
```python dnsproxy.py -m non-sni```
The generator will create these three files:
- output/haproxy.conf
- output/dnsmasq-haproxy.conf
- output/iptables-haproxy.sh

#### local (Advanced Setup)

Local mode enables DNS-unblocking on a single device which can't handle SNI but only uses a single IP address and without using another server on the network.
Use the generator as follows:
```python dnsproxy.py -m local```

The generator will create the following files:
- output/haproxy.conf (for the remote server)
- output/netsh-haproxy.cmd (for Windows)
- output/rinetd-haproxy.conf (for Linux)
- output/hosts-haproxy.txt (for Linux/Windows)

For Windows:
- Run notepad as administrator and open `%SystemRoot%\system32\drivers\etc\hosts` (usually `c:\windows\system32\drivers\etc\hosts`), append the contents of `hosts-haproxy.txt`
- Run `netsh-haproxy.cmd` as administrator
- To reset: delete contents of `%SystemRoot%\system32\drivers\etc\hosts`, run as administrator `netsh interface portproxy reset`

For Linux:
- Run `sudo tee -a /etc/hosts < hosts-haproxy.txt` (or append hots-haproxy.txt to /etc/hosts)
- Run `sudo cp rinetd-haproxy.conf /etc/rinetd.conf && sudo service rinetd start`
- To reset: `sudo sed -i '/### GENERATED/d' /etc/hosts` and `sudo service rinetd stop && sudo rm /etc/rinetd.conf`

