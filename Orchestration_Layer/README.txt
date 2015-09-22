  In today’s world, Hypervisor is the new OS and Virtual Machines are the new processes. Many system programmers are familiar with the low level APIs that are exposed by the operating systems like Linux and Microsoft Windows. These APIs can be used to take control of the OS programmatically and help in developing management tools. Similar to the OS, Hypervisors expose APIs that can be invoked to manage the virtualized environments. Typical APIs include provisioning, de­provisioning, changing the state of VMs, configuring the running VMs and so on. While it may be easy to deal with one Hypervisor running on a physical server, it is complex to concurrently deal with a set of Hypervisors running across the datacenter. In a dynamic environment, this is a critical requirement to manage the resources and optimize the infrastructure. This is the problem that we try to solve in this project. 
  
  We build a fabric that can coordinate the provisioning of compute resources by negotiating with a set of Hypervisors running across physical servers in the datacenter. 

>>> A GUI is created to facilitate the client to easily create and manange his virtual machines.
>>> To set up the server run the command ./bin/script pm_file image_file flavor_file
>>> Then open the page create.html in src to start interactive operations.
