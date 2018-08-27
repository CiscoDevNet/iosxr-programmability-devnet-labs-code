#!/bin/bash

r1_user="admin"
r1_port=2222
r1_ip="10.10.20.170"

r2_user="admin"
r2_port=2232
r2_ip="10.10.20.170"

function reset_config() {

  router=$1
  r_user=$2
  r_port=$3
  r_ip=$4

  # Transfer file to the router
  scp -P $r_port -o StrictHostKeyChecking=no ./configs/router_reset_$router.conf ${r_user}@$r_ip:/home/admin/router_reset.conf

  source_library="source /pkg/bin/ztp_helper.sh"
  bash_cmd="$source_library && xrapply /home/admin/router_reset.conf"
  priv_escalate="sudo -i /bin/bash -c"

  timeout 45 ssh -t -o StrictHostKeyChecking=no -p $r_port ${r_user}@$r_ip "$priv_escalate '$bash_cmd'"

  echo "Configuration done!"

  xrcmd_cmd="show running-config"
  bash_cmd="$source_library && xrcmd $xrcmd_cmd"

  echo "Verifying loopback1 configuration..."  
  ssh -t -o StrictHostKeyChecking=no -p $r_port ${r_user}@$r_ip "$priv_escalate '$bash_cmd'"

}


# Reset Configuration
reset_config "r1" $r1_user $r1_port $r1_ip

reset_config "r2" $r2_user $r2_port $r2_ip

