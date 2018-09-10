#!/usr/bin/env python

import sys
sys.path.append("/pkg/bin")
from ztp_helper import ZtpHelpers
from pprint import pprint

loopback2_config="""!
                    interface loopback2
                    ipv4 address 100.100.100.100/32
                    !
                    end
                 """


ztp_obj = ZtpHelpers()

response = ztp_obj.xrapply_string(cmd=loopback2_config)

pprint(response)
