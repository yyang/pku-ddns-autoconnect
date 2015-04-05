#!/usr/bin/env python
#
# Package: PKU DDNS Auto Connect
# File:    autoconnect.py
# Author:  Yi Yang
#
# Copyright (c) 2015 Yi Yang <me@iyyang.com>.

import os
import sys
import socket
import fcntl
import struct
import subprocess
import logging, logging.handlers

if sys.version_info[0] < 3:
  from ConfigParser import ConfigParser
else:
  from configparser import ConfigParsers

class AutoConnException(Exception):
  pass

"""
  Defines logger and stores log files on a rotation basis.
"""

current_path = os.path.dirname(os.path.abspath(__file__))
config_file  = os.path.join(current_path, 'config')
status_file  = os.path.join(current_path, 'status')
ipgw_script  = os.path.join(current_path, 'ipgw/pkuipgw/pkuipgw')
log_path     = os.path.join(current_path, 'log')
log_file     = os.path.join(log_path, 'autoconnect.log')

if not os.path.exists(log_path):
    os.makedirs(log_path)

logger    = logging.getLogger('autoconnect')
handler   = logging.handlers.TimedRotatingFileHandler(log_file, when = 'D', 
                                                      interval = 1, 
                                                      backupCount = 14)
formatter = logging.Formatter('%(asctime)s - [%(name)s] - %(message)s')

handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


"""
  The following scripts are used to testify the network availability.
"""

def ping_website(website):
  try:
    # see if we can resolve the host name -- tells us if there is
    # a DNS listening
    host = socket.gethostbyname(website)
    # connect to the host -- tells us if the host is actually reachable
    s = socket.create_connection((host, 80), 2)
    logger.info(website + ' is available')
    return True
  except:
    pass
  logger.info(website + ' is NOT available')
  return False

def ping_network():
  if not ping_website('www.pku.edu.cn'):
    raise AutoConnException('NetworkError', 'Seems Internet is not available.')
  cernet_free_available = ping_website('www.baidu.com')
  global_available      = ping_website('www.acs.org')
  return (cernet_free_available and global_available)

"""
  Invokes PKU IPGW connection script
"""

def disconnect_ipgw(all = False):
  disconnect_ipgw_command = ipgw_script + ' -c ' + config_file + ' connect'
  if all:
    disconnect_ipgw_command += ' all'
  p = subprocess.Popen(disconnect_ipgw_command, shell=True, 
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  out, err = p.communicate()
  if out.find('Error') != -1:
    logger.error(out.replace('\n', ' @@'));
    raise AutoConnException('IpgwError', 'Failed to disconnect.')

def connect_ipgw(scope):
  connect_ipgw_command = ipgw_script + ' -c ' + config_file + ' connect'
  if scope == 'global'
    connect_ipgw_command += ' all'
  p = subprocess.Popen(connect_ipgw_command, shell=True, 
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  out, err = p.communicate()
  if out.find('Error') != -1:
    logger.error(out.replace('\n', ' @@'));
    raise AutoConnException('IpgwError', 'Failed to connect.')

"""
  Updates DDNS
"""

def get_ip_address(ifname):
  if sys.platform == 'darwin':
    return socket.gethostbyname(socket.gethostname())
  elif sys.platform == 'linux2':
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
      s.fileno(),
      0x8915,  # SIOCGIFADDR
      struct.pack('256s', ifname[:15])
    )[20:24])
  else:
    raise AutoConnException('SystemError', 
                            'OS `' + sys.platform + '`Not Supported.')

def update_ddns(ddns, ip_address):
  if ddns['provider'] == 'pubyun':
    update_url = 'http://members.3322.net/dyndns/update?system=dyndns&hostname='
    update_ddns_command = 'lynx -mime_header -auth=' + ddns['username'] + \
                          ':' +  ddns['password'] + ' "' + update_url + \
                          ddns['domain'] + '"'
    p = subprocess.Popen(update_ddns_command, shell=True, 
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out, err = p.communicate()
    logger.info(out.replace('\n', ' @@'));
  else: 
    raise AutoConnException('DdnsError', 'Provider not supported.')

"""
  Main function
"""

def read_config():
  config = ConfigParser()
  if not config.read(config_file):
    raise AutoConnException('ConfigFileError', 'Configuration file missing.')
  elif 'ddns' not in config.sections():
    raise AutoConnException('ConfigFileError', 'Missing section `ddns`.')
  elif 'connect' not in config.sections():
    raise AutoConnException('ConfigFileError', 'Missing section `connect`.')
  return config

def read_status():
  status = ConfigParser()
  if not status.read(status_file):
    raise AutoConnException('StatusFileError', 'Status file missing.')
  return status

def main():
  logger.info('Started PKU DDNS Auto Connect.')
  try:
    config = read_config()
    status = read_status()

    if not ping_network():
      disconnect_ipgw()
      connect_ipgw(config._sections['connect']['scope'])
      ping_network()

    current_ip = get_ip_address(config._sections['connect']['interface'])
    if not status._sections['ddns']['system_ip'] == current_ip:
      update_ddns(config._sections['ddns'], current_ip)

  except AutoConnException as ex:
    sys.stderr.write('%s: %s\n' % tuple(ex.args))
  logger.info('Terminated.\n')


if __name__ == '__main__':
  main();