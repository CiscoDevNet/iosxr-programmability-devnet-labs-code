#!/bin/bash
source ./connection_details.sh

function reset_config() {

  router=$1
  r_user=$2
  r_password=$3
  r_port=$4
  r_ip=$5

  echo -ne "\nStarting Reset process for Router $router....\n"
  # Transfer file to the router
  sshpass -p $r_password scp -P $r_port -o StrictHostKeyChecking=no ./configs/router_reset_$router.conf ${r_user}@$r_ip:/home/admin/router_reset.conf 2>&1 >/dev/null
  sleep 2
  source_library="source /pkg/bin/ztp_helper.sh"
  bash_cmd="$source_library && xrreplace /home/admin/router_reset.conf"
  priv_escalate="sudo -i /bin/bash -c"

  timeout 45 sshpass -p $r_password ssh -t -o StrictHostKeyChecking=no -p $r_port ${r_user}@$r_ip "$priv_escalate '$bash_cmd'" 2>&1 > /dev/null
  sleep 2
  echo "Configuration done!"

  xrcmd_cmd="show running-config"
  bash_cmd="$source_library && xrcmd $xrcmd_cmd"

  echo "Verifying running configuration..."  
  running_config=`sshpass -p $r_password ssh -t -o StrictHostKeyChecking=no -p $r_port ${r_user}@$r_ip "$priv_escalate '$bash_cmd'"`
  running_config=`echo "$running_config" | tail -n +4`
  echo "$running_config" > current_running_config_$router

  #expected_config=`cat ./configs/router_reset_$router.conf`

  compare_result=`cmp --silent ./current_running_config_$router  ./configs/router_reset_$router.conf` 
  if ! [[ "$compare_result" ]]; then
      echo -ne "Configuration Successful!\n\n"
      rm -f current_running_config_$router
  else
      echo "Failed to apply configuration"
      echo "Current configuration: "
      echo -ne "$running_config\n\n\n"
  fi

}


# Reset Configuration
reset_config "r1" $r1_user $r1_password $r1_port $r1_ip

reset_config "r2" $r2_user $r2_password $r2_port $r2_ip
