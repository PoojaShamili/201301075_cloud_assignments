 Steps to follow:
  >> Start the pox server by giving the following command:
"sudo python pox.py forwarding.l2_multi openflow.discovery --eat-early-packets openflow.spanning_tree --no-flood --hold-down"
  >> In another terminal, run:
"sudo python 201301075.py" and enter the number of hosts and switches.
  >> Once the CLI for mininet comes up, perform "pingall" to test connectivity between hosts.
