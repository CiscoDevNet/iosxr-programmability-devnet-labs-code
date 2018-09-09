#!/usr/bin/env python

import sys
sys.path.append("/pkg/bin/")
from ztp_helper import ZtpHelpers

ParameterMap = { 
                  "rtr1" : {
                             "local_asn" : 65000,
                             "remote_asn" : 65000,
                             "loopback0_ip" : "1.1.1.1/32",
                             "bgp_neighbor_ip" : "2.2.2.2"
                           },

                  "rtr2" : {
                             "local_asn" : 65000,
                             "remote_asn" : 65000,
                             "loopback0_ip" : "2.2.2.2/32",
                             "bgp_neighbor_ip" : "1.1.1.1"
                           }
               }


class ZtpChildClass(ZtpHelpers):

    def get_hostname(self):

        show_command= "show running-config hostname"
      
        response = self.xrcmd({"exec_cmd" : show_command})

        if response["status"] == "success":
            try:
                output = response["output"]
                hostname_config = output[0]
                hostname = hostname_config.split()[1] 
                return hostname
            except Exception as e:
                print("Failed to extract hostname")
                print("Error: " + str(e))
                sys.exit(1) 
        else:
            print("Failed to fetch hostname configuration")
            sys.exit(1)


    def configure_ospf(self) {

        ospf_config = """!
                         router ospf ztp-bash
                           area 0
                             interface Loopback0
                             !
                             interface GigabitEthernet0/0/0/0
                             !
                             interface GigabitEthernet0/0/0/1
                             !
                           !
                         !
                         end
                      """

    }


    def configure_bgp(asn=None, hostname=None) {
        
        bgp_config = """ !
                         router bgp {local_asn}
                           address-family ipv4 unicast
                         !
                         neighbor {neighbor_ip}
                           remote-as {remote_asn}
                           update-source Loopback0
                           address-family ipv4 unicast
                           !
                         !
                         end
                      """.format(local_asn = ParameterMap[hostname][local_asn],
                                 neighbor_ip = ParameterMap[hostname][bgp_neighbor_ip],
                                 remote_asn = ParameterMap[hostname][remote_asn])

    }


    def configure_loopback() {

        hostname = self.get_hostname()
        loopback0_config = """!
                              interface Loopback0
                                ipv4 address ${HostMap[${hostname}]}
                              !
                              end
                           """

    }
