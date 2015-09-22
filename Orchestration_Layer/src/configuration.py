from flask import Flask
from flask.ext.restful import Api, Resource
from flask import request
from flask import jsonify
import libvirt
from flask_cors import CORS
from lxml import etree
import uuid
import sys, os, ast
import Queue

app = Flask(__name__)
api = Api(app)
cors = CORS(app)

created_vms = {}
pm_list = []
image_list = []
chosen_pms = {}
queue = Queue.Queue()
vm_types = {}

def Scheduler(cpu, ram, disk):
    for pm_id in range(len(pm_list)):
        pm = pm_list[pm_id]
        cmnd1 = "ssh " + pm + " free -k | grep 'Mem:' | awk '{ print $4}' > output"
        cmnd2 = "ssh " + pm + " nproc >> output"
        cmnd3 = "ssh " + pm + " df -h --total | grep total | awk '{ print $2}' >> output"
        os.system(cmnd1)
        os.system(cmnd2)
        os.system(cmnd3)
        fp = open('output', 'r')
        new_ram = int(fp.readline())
        new_cpu = int(fp.readline())
        new_disk = str(fp.readline())
        l = new_disk.strip('/n')
        i_new_disk = l[:-1]
        if disk  < i_new_disk:
            if ram < new_ram:
                if cpu < new_cpu:
                    return pm_id
    #####implement queue###########
    try:
        vm_id = queue.get_nowait()
        pm_id = created_vms[vm_id]['pm_id']
        pm = pm_list[pm_id]
        conn = libvirt.open("qemu+ssh://" + str(pm) + "/system")
        dom = conn.lookupByID(vm_id)
        if dom.isActive():
            dom.destroy()
        dom.undefine()
        del created_vms[vm_id]
        return pm_id
    except:
        return -1

def send_image(pm, image_path):
    url = image_path.split(':')[1]
    path = '/home/' + pm.split('@')[0] + '/' + url.split('/')[-1]
    cmnd1 = 'ssh ' + pm + ' rm ' + path
    cmnd2 = 'scp ' + image_path + ' ' + pm + ':/home/' + pm.split('@')[0] + '/'
    try:
        os.system(cmnd1)
    except:
        pass
    os.system(cmnd2)
    return path

@app.route('/vm/create', methods=['GET'])
def create_vm():
    n = str(request.args.get('name'))
    new_instance_type = int(request.args.get('instance_type'))
    image_id = int(request.args.get('image_id'))
    new_cpu = int(vm_types[new_instance_type]['cpu'])
    new_ram = int(vm_types[new_instance_type]['ram'])
    new_disk = int(vm_types[new_instance_type]['disk'])
    i = str(uuid.uuid1())
    image_path = image_list[image_id]
    short_image_path = image_path.split(':')[1]
    pm_id = Scheduler(new_cpu, new_ram, new_disk)
    pm = pm_list[pm_id]
    if pm == -1:
        return jsonify({"Error" : " Specifications could not be satisfied, Virtual Machine cannot be created" })
    #path = send_image(pm, image_path)
    xml = """<domain type='qemu' id='%s'><name>%s</name><memory>%s</memory> <currentMemory>512000</currentMemory> <vcpu>%s</vcpu> <os> <type arch='i686' machine='pc-1.0'>hvm</type> <boot dev='hd'/> </os> <features> <acpi/> <apic/> <pae/> </features> <clock offset='utc'/> <on_poweroff>destroy</on_poweroff> <on_reboot>restart</on_reboot> <on_crash>restart</on_crash> <devices> <emulator>/usr/bin/qemu-system-i386</emulator> <disk type='file' device='disk'> <driver name='qemu' type='raw'/> <source file='%s' /> <target dev='hda' bus='ide'/> <alias name='ide0-0-0'/> <address type='drive' controller='0' bus='0' unit='0'/> </disk> <controller type='ide' index='0'> <alias name='ide0'/> <address type='pci' domain='0x0000' bus='0x00' slot='0x01' function='0x1'/> </controller> <interface type='network'> <mac address='52:54:00:82:f7:43'/> <source network='default'/> <target dev='vnet0'/> <alias name='net0'/> <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/> </interface> <serial type='pty'> <source path='/dev/pts/2'/> <target port='0'/> <alias name='serial0'/> </serial> <console type='pty' tty='/dev/pts/2'> <source path='/dev/pts/2'/> <target type='serial' port='0'/> <alias name='serial0'/> </console> <input type='mouse' bus='ps2'/> <graphics type='vnc' port='5900' autoport='yes'/> <sound model='ich6'> <alias name='sound0'/> <address type='pci' domain='0x0000' bus='0x00' slot='0x04' function='0x0'/> </sound> <video> <model type='cirrus' vram='9216' heads='1'/> <alias name='video0'/> <address type='pci' domain='0x0000' bus='0x00' slot='0x02' function='0x0'/> </video> <memballoon model='virtio'> <alias name='balloon0'/> <address type='pci' domain='0x0000' bus='0x00' slot='0x05' function='0x0'/> </memballoon> </devices> <seclabel type='dynamic' model='apparmor' relabel='yes'> <label>libvirt-10a963ef-9458-c30d-eca3-891efd2d5817</label> <imagelabel>libvirt-10a963ef-9458-c30d-eca3-891efd2d5817</imagelabel> </seclabel></domain>""" % (i, n, str(int(new_ram)*1000), str(new_cpu), short_image_path)
    virConnect_obj = libvirt.open("qemu+ssh://" + str(pm) + "/system")
    virDomain_obj = virConnect_obj.defineXML(xml)
    status = virDomain_obj.create()
    j = virDomain_obj.ID()
    if status == 0:
        created_vms[j] = {'obj' : virDomain_obj, 'instance_type' : new_instance_type, 'pm_id' : pm_id, 'name' : n}
        queue.put_nowait(j)
        try:
            chosen_pms[pm_id].append(j)
        except:
            chosen_pms[pm_id] = [j]
        return jsonify(vmid=j)
    else:
        return 0

@app.route('/vm/query', methods=['GET'])
def vm_query():
    new_id = int(request.args.get('vmid'))
    name = created_vms[new_id]['name']
    instance_type = created_vms[new_id]['instance_type']
    pm_id = created_vms[new_id]['pm_id']
    temp = {"vmid" : new_id, "name" : name, "instance_type" : instance_type, "pmid" : pm_id}
    return jsonify(temp)

@app.route('/vm/destroy',methods=['GET'])
def destroy_vm():
    vm_id = int(request.args.get('vmid'))
    try:
        pm_id = created_vms[vm_id]['pm_id']
        pm = pm_list[pm_id]
        conn = libvirt.open("qemu+ssh://" + str(pm) + "/system")
        dom = conn.lookupByID(vm_id)
        if dom.isActive():
            dom.destroy()
        dom.undefine()
        del created_vms[vm_id]
        for i in range(len(chosen_pms[pm_id])):
            if chosen_pms[pm_id][i] == vm_id:
                chosen_pms[pm_id].pop(i)
        return jsonify(status=1)
    except:
        return jsonify(status=0)

@app.route('/vm/types', methods=['GET'])
def get_types():
    dic = {"types": vm_types}
    return jsonify(dic)

@app.route('/pm/list', methods=['GET'])
def list_pms():
    seq = range(len(pm_list))
    return jsonify(pmids=seq)

@app.route('/pm/listvms', methods=['GET'])
def list_vms():
    pm_id = int(request.args.get('pmid'))
    x = chosen_pms[pm_id]
    return jsonify(vmids=x)

@app.route('/pm/query', methods=['GET'])
def pm_query():
    pm_id = int(request.args.get('pmid'))
    pm = pm_list[pm_id]
    cmnd1 = "ssh " + pm + " free -m | grep 'Mem:' | awk '{print $2}' > data1"
    cmnd2 = "ssh " + pm + " lscpu | grep 'CPU(s):' | awk '{print $2}' >> data1"
    cmnd3 = "ssh " + pm + " df -h --total | grep total | awk '{print $2}' >> data1"
    os.system(cmnd1)
    os.system(cmnd2)
    os.system(cmnd3)
    fp = open('data1', 'r')
    tot_ram = int(fp.readline())
    tot_cpu = int(fp.readline())
    tot_disk = str(fp.readline())
    l = tot_disk[:-2]
    i_tot_disk = int(l)
    print l, i_tot_disk
    cmnd1 = "ssh " + pm + " free -m | grep 'Mem:' | awk '{ print $4}' > data2"
    cmnd2 = "ssh " + pm + " nproc >> data2"
    cmnd3 = "ssh " + pm + " df -h --total | grep total | awk '{print $4}' >> data2"
    os.system(cmnd1)
    os.system(cmnd2)
    os.system(cmnd3)
    fp = open('data2', 'r')
    new_ram = int(fp.readline())
    new_cpu = int(fp.readline())
    new_disk = str(fp.readline())
    l = new_disk[:-2]
    i_new_disk = int(l)
    temp = {}
    temp['pmid'] = pm_id
    temp1 = {}
    temp1['cpu'] = tot_cpu
    temp1['ram'] = tot_ram
    temp1['disk'] = i_tot_disk
    temp['capacity'] = temp1
    temp2 = {}
    temp2['cpu'] = new_cpu
    temp2['ram'] = new_ram
    temp2['disk'] = i_new_disk
    temp['free'] = temp2
    temp['vms'] = len(chosen_pms[pm_id])
    return jsonify(temp)

@app.route('/image/list', methods=['GET'])
def list_images():
    images = []
    for i in range(len(image_list)):
        name = (image_list[i].split('/')[-1]).split('.')[0]
        images.append({'id': i, 'name': name})
    return jsonify(images=images)
def create_pm_list(pm_file):
    fp = open(pm_file, 'r')
    for line in fp:
        global pm_list
        line = line.strip('\n')
        pm_list.append(line)

def create_img_list(img_file):
    fp = open(img_file, 'r')
    for line in fp:
        global image_list
        line = line.strip('\n')
        image_list.append(line)

def create_vm_types(flavor_file):
    fp = open(flavor_file, 'r')
    y = fp.read()
    y = y.replace(' ', '')
    y = y.replace('\n', '')
    global vm_types
    old_vm_types = ast.literal_eval(y)
    vm_types = old_vm_types['types']

if __name__ == '__main__':
    create_pm_list(sys.argv[1])
    create_img_list(sys.argv[2])
    create_vm_types(sys.argv[3])
    app.run(host='0.0.0.0',port=1235,debug=True,threaded=True)
