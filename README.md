dnsproxy
========

This is heavily based on @trick77's original work on [tunlr-style-dns-unblocking](https://github.com/trick77/tunlr-style-dns-unblocking/)

Prerequisites:
- python
- haproxy

For `pure-sni` and `non-sni`:
- dnsmasq


THIS IS NOT A TUTORIAL!

The configuration generator (genconf.py) offers three different modes:
- pure-sni (Simple Setup)
- non-sni (Advanced Setup)
- local (Advanced Setup)

See here for additional information: 

- http://trick77.com/2014/03/01/tunlr-style-dns-unblocking-pandora-netflix-hulu-et-al/
- http://trick77.com/2014/03/02/dns-unblocking-using-dnsmasq-haproxy/

Here's a tester which may help while deploying your own DNS unblocking solution:
http://trick77.com/dns-unblocking-setup-tester/

If you would like to add a service, please send a pull request.

Usage: 
```
genconf.py [-h] [-m {pure-sni,non-sni,local}] [--dnsmasq DNSMASQ]
                  [--haproxy HAPROXY] [--iptables IPTABLES] [--netsh NETSH]
                  [--hosts HOSTS] [--rinetd RINETD] [--ip IP]
                  [--bind-ip BIND_IP] [--save] [--base-dir BASE_DIR]
                  [--skip [{dnsmasq,haproxy,netsh,hosts,rinetd} [{dnsmasq,haproxy,netsh,hosts,rinetd} ...]]]

Generate configuration files to setup a tunlr style smart DNS

optional arguments:
  -h, --help            show this help message and exit
  -m {pure-sni,non-sni,local}, --mode {pure-sni,non-sni,local}
                        The mode of configuration files to generate
  --dnsmasq DNSMASQ     Specify the DNS configuration file name
  --haproxy HAPROXY     Specify the haproxy configuration file name
  --iptables IPTABLES   Specify the iptables configuration file name
  --netsh NETSH         Specify the netsh configuration file name
  --hosts HOSTS         Specify the hosts configuration file name
  --rinetd RINETD       Specify the rinetd configuration file name
  --ip IP               Specify the public ip to use
  --bind-ip BIND_IP     Specify the ip that haproxy should bind to
  --save                Specify wether to save the configuration
  --base-dir BASE_DIR   Specify the output directory
  --skip [{dnsmasq,haproxy,netsh,hosts,rinetd} [{dnsmasq,haproxy,netsh,hosts,rinetd} ...]]
                        Specify the configurations to skip
 ```
#### pure-sni (Simple Setup)

This is also the default option.

Use this setup if all your multimedia players are SNI-capable. (This is usually the case.)

Requires a U.S. based server (a 128 MB low end VPS is enough) and preferrably a local Dnsmasq DNS forwarder. DD-WRT routers or a Raspberry Pi will do. You can run Dnsmasq on the remote server as well but please be aware of the security and latency issues.

In pure-sni mode, you don't have to worry about the `base_ip` and the `base_port` options. Those options are not used, just leave them at their defaults. Make sure `iptables_location` points to the iptables executable and enter your VPS' IP address in `public_ip`. Make sure the ports 80 and 443 on your VPS are not being used by some other software like Apache2. Use ```netstat -tulpn``` to make sure.

For this mode, call the generator like this:
```python genconf.py```

The generator will create two files based on the information in config.json:
- generated/haproxy.conf
- generated/dnsmasq-haproxy.conf
 
#### non-sni (Advanced Setup)

non-sni mode enables DNS-unblocking for multimedia players (or applications) which can't handle SNI but still using just a single IP address using some netfilter trickery. See here for more information on this mode:
http://trick77.com/2014/04/02/netflix-dns-unblocking-without-sni-xbox-360-ps3-samsung-tv/

Test your new setup with http://trick77.com/dns-unblocking-setup-tester/

Non-conclusive list of devices which don't understand SNI:
- Xbox 360 
- PS3
- All Sony Bravia TVs and Blu-ray players 
- Older Samsung TVs

The generator will create three files based on the information in config.json:
- generated/haproxy.conf
- generated/dnsmasq-haproxy.conf
- generated/iptables-haproxy.sh

#### local (Advanced Setup)

local mode enables DNS-unblocking on a single device which can't handle SNI but still using just a single IP address and without using another server on the network.
The generator will create four files based on the information in json.config:
- generated/haproxy.conf (for the remote server)
- generated/netsh-haproxy.cmd (for Windows)
- generated/rinetd-haproxy.conf (for Linux)
- generated/hosts-haproxy.txt (for Linux/Windows)

For Windows:
- Run notepad as administrator and open %SystemRoot%\system32\drivers\etc\hosts (usually c:\windows\system32\drivers\etc\hosts), append the contents of hosts-haproxy.txt
- Run netsh-haproxy.cmd as administrator

- To reset: delete contents of %SystemRoot%\system32\drivers\etc\hosts, run as administrator 'netsh interface portproxy reset'

For Linux:
- Run 'sudo tee -a /etc/hosts < hosts-haproxy.txt' (or append hots-haproxy.txt to /etc/hosts)
- Run 'sudo cp rinetd-haproxy.conf /etc/rinetd.conf && sudo service rinetd start'

- To reset: 'sudo sed -i '/### GENERATED/d' /etc/hosts' and 'sudo service rinetd stop && sudo rm /etc/rinetd.conf'

