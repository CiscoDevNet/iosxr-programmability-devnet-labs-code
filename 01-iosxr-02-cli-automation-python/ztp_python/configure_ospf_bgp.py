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
                return "" 
        else:
            print("Failed to fetch hostname configuration")
            return ""


    def configure_ospf(self) {

        ospf_config = """!
                         router ospf ztp-python
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
    
        try:
            response = self.xrapply_string(cmd=ospf_config)

            if response["status"] == "success":
                print("OSPF configuration successfully applied")
                print(response["output"])
                return True
            else:
                print("Failed to apply OSPF configuration")
                print(response["output"])
                return False
        except Exception as e:
            print("Failed to apply OSPF configuration")
            print("Error : "+str(e))
            return False
    }


    def configure_bgp(asn=None, hostname=None) {

        hostname = self.get_hostname() 
 
        if hostname == "":
            print("Require hostname to determine bgp config, aborting")
            return False

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

        with open("/tmp/bgp_config", 'w') as fd:
            fd.write(bgp_config)

        try:
            response = self.xrapply(filename="/tmp/bgp_config")
            os.remove("/tmp/bgp_config")

            if response["status"] == "success":
                print("BGP configuration successfully applied")  
                print(response["output"])
                return True
            else:
                print("Failed to apply BGP configuration")  
                print(response["output"])
                return False         
        except Exception as e:
            print("Failed to apply BGP configuration")
            print("Error : "+str(e))
            os.remove("/tmp/bgp_config")
            return False
    }


    def configure_loopback(self) {

        hostname = self.get_hostname()

        if hostname == "":
            print("Require hostname to determine bgp config, aborting")
            return False

        loopback0_config = """!
                              interface Loopback0
                                ipv4 address {loopback0_ip}
                              !
                              end
                           """.format(loopback0_ip = ParameterMap[hostname][loopback0_ip])

        try:
            response = self.xrapply_string(cmd=loopback0_config)

            if response["status"] == "success":
                print("Loopback0 configuration successfully applied")
                print(response["output"])
                return True
            else:
                print("Failed to apply Loopback0 configuration")  
                print(response["output"]) 
                return False
        except Exception as e:
            print("Failed to apply Loopback0 configuration")
            print("Error : "+str(e))
            return False
    
    }


if __name__ == "__main__":

    config_obj = ZtpChildClass()

    if not config_obj.configure_loopback():
        print("Couldn't apply loopback0 configuration, aborting")
        sys.exit(1)
 
    if not config_obj.configure_ospf():
        print("Couldn't apply ospf configuration, aborting")
        sys.exit(1)

    if not config_obj.configure_bgp():
        print("Couldn't apply bgp configuration, aborting")
        sys.exit(1)

    sys.exit(0)
