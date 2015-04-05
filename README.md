PKU DDNS Auto Connect
=====================

## Overview

This package connects PKU IPGW and updates Dynamic DNS service when internet is
available.

## Installation

The configurations are stored in `config`, and a template is available in
`config.tmpl`. All items are required, and you may further test run via 
`./autoconnect.py`. The script will create a `log` folder and store logs on 
rotation basis.

We may check IPGW status and reconnect / update DDNS on a routine basis. We may
set up a root crontab to run the script regularly. Cron could be installed via 
the following command:

```shell
# el7
yum install cronie
systemctl start crond.service
systemctl enable crond.service
# el6
yum install cronie
service crond start
chkconfig crond on
# debian
apt-get install cron
service crond start
chkconfig crond on
```

When corn is installed and enabled during boot, we may further setup crontabs
via `sudo crontab -e` (__must__ use `sudo` to run at reboot). The following 
cron tabs might be helpful.

```
# executes while reboot
@reboot /path/to/autoconnect.py
# executes every 5 minutes
*/5 * * * * /path/to/autoconnect.py
```

## Dependencies and Acknowledgements

### PKU IPGW Client for Linux

Version: 0.4.1, included in the repo.

PKU IPGW Client for Linux is open sourced by Chen Xing and Casper Ti. Vector, 
and we are using it _as is_.

Thanks for their efforts.
