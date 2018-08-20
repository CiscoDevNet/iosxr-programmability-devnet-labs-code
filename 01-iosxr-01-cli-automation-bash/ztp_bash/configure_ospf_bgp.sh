#!/bin/bash
source /pkg/bin/ztp_helper.sh

# Creating an associative array for hostname<-->loopback_ip

declare -A HostMap

HostMap["r1"]="1.1.1.1/32"
HostMap["r2"]="2.2.2.2/32"

declare -A NeighborMap

NeighborMap["r1"]="2.2.2.2"
NeighborMap["r2"]="1.1.1.1"

IbgpASN=65000

function get_hostname() {

    # Fetch hostname from XR CLI
    output=`xrcmd "show running-config hostname"`

    # Extract hostname from XR CLI output result
    # (Removing the string "hostname" and removing whitespace)

    hostname=`echo $output | head -2 | sed -e "s/^hostname//" | xargs echo -n`
}

function configure_ospf() {

read -r -d '' ospf_config << EOF
    !
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
EOF

    xrapply_string "$ospf_config" > /dev/null

    if [[ $? != 0 ]]; then
        echo "Failed to apply ospf configuration"
        xrcmd "show configuration failed"
        exit 1
    else
        echo "OSPF Configuration successful!"
        xrcmd "show configuration commit changes last 1"
    fi
}

function configure_bgp() {
    asn=$1
    hostname=$2

    # Extract the neighbor from hostname using the NeighborMap

cat > /tmp/bgp_config << EOF
    !
    router bgp $asn
     address-family ipv4 unicast
    !
    neighbor ${NeighborMap[${hostname}]}
      remote-as $asn
      update-source Loopback0
      address-family ipv4 unicast
      !
     !
    !
   end
EOF
    

    # Here we utilize the xrapply_with_reason utility
    xrapply_with_reason "iBGP config using xrapply_with_reason" /tmp/bgp_config > /dev/null

    if [[ $? != 0 ]]; then
        echo "Failed to apply BGP configuration"
        xrcmd "show configuration failed"
        # Remove BGP config /tmp file
        rm -f /tmp/bgp_config    
        exit 1
    else
        echo "BGP Configuration successful!"
        xrcmd "show configuration commit changes last 1"
        rm -f /tmp/bgp_config
    fi


}


function configure_loopback() {

    # Fetch hostname
    get_hostname
    
    # Based on the hostname variable now set, extract the loopback address from HostMap

read -r -d '' loopback0_config << EOF
    !
    interface Loopback0
      ipv4 address ${HostMap[${hostname}]}
    !
    end
EOF

    #configure Loopback address
    xrapply_string "$loopback0_config" > /dev/null

    if [[ $? != 0 ]]; then
        echo "Failed to apply Loopback0 configuration"
        xrcmd "show configuration failed"
        exit 1
    else
        echo "Loopback0 Configuration successful!"
        xrcmd "show configuration commit changes last 1"
    fi

}


configure_loopback
configure_ospf
configure_bgp $IbgpASN $hostname
