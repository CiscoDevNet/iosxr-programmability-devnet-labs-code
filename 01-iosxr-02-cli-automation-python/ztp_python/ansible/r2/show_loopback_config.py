#!/usr/bin/env python

import sys
sys.path.append("/pkg/bin")
from ztp_helper import ZtpHelpers
from pprint import pprint

ztp_obj = ZtpHelpers()

response = ztp_obj.xrcmd({"exec_cmd" : "show running-config interface loopback2"})

pprint(response)
