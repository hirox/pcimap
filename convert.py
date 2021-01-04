desc = 'Convert lspci output to plantuml'

import sys
import re
import argparse

parser = argparse.ArgumentParser(description=desc)
parser.add_argument('-m', '--markdown', action='store_true')
args = parser.parse_args()

def to_bd_node(f):
    return "node" + f["bus"] + "_" + f["device"]

def to_bdf_node(f):
    return "node" + f["bus"] + "_" + f["device"] + "_" + f["func"]

def link(devices, current):
    bus = int(current["bus"], 16)
    last = 0
    parent = None
    for key in devices.keys():
        fs = devices[key]
        for f in fs:
            if f["is_pci_bridge"]:
                if f["child_from"] <= bus and bus <= f["child_to"]:
                    if last < f["child_from"]:
                        last = f["child_from"]
                        parent = f

    annotation = ""
    if current.get("cap_speed") and current.get("cap_width"):
        speed_to_str = {"2.5GT/s": "2.5GT/s (Gen1)", 
                        "5GT/s": "5GT/s (Gen2)",
                        "8GT/s": "8GT/s (Gen3)",
                        "16GT/s": "16GT/s (Gen4)",
                        "32GT/s": "32GT/s (Gen5)",
                        "64GT/s": "64GT/s (Gen6)"}
        cap_speed = current["cap_speed"]
        if speed_to_str.get(cap_speed):
            cap_speed = speed_to_str[cap_speed]
        annotation = " : Capability " + cap_speed + ", " + current["cap_width"]

        if current.get("sta_speed") and current.get("sta_width"):
            sta_speed = current["sta_speed"]
            if speed_to_str.get(sta_speed):
                sta_speed = speed_to_str[sta_speed]
            annotation = annotation + "\\n Status " + sta_speed + ", " + current["sta_width"]

    from_node = "root"
    if parent:
        from_node = to_bdf_node(parent)

    print('{} --> {}{}'.format(from_node, to_bdf_node(current), annotation))

is_pci_bridge = False

if args.markdown:
    print("```plantuml")

print("@startuml")
print("left to right direction")
print("rectangle root")

devices = {}
current = {}
for l in sys.stdin:
    m = re.match(r'([\da-f]+):([\da-f]+)\.([\da-f])\s+(.+)', l)
    if m:
        f = {}
        f["bus"] = m[1]
        f["device"] = m[2]
        f["func"] = m[3]
        f["desc"] = m[4]

        if re.match(r'^PCI bridge:', f["desc"]):
            is_pci_bridge = True
        else:
            is_pci_bridge = False

        f["is_pci_bridge"] = is_pci_bridge

        bd = f["bus"] + ":" + f["device"]
        if devices.get(bd):
            devices[bd].append(f)
        else:
            devices[bd] = [f]

        current = f
    else:
        if is_pci_bridge:
            m = re.match(r'\s+Bus: primary=([\da-f]+), secondary=([\da-f]+), subordinate=([\da-f]+)', l)
            if m:
                current["child_from"] = int(m[2], 16)
                current["child_to"] = int(m[3], 16)

        m = re.match(r'\s+LnkCap:.+Speed ([\w\.]+?/s).*? Width (x\d+)', l)
        if m:
            current["cap_speed"] = m[1]
            current["cap_width"] = m[2]

        m = re.match(r'\s+LnkSta:.+Speed ([\w\.]+?/s).*? Width (x\d+)', l)
        if m:
            current["sta_speed"] = m[1]
            current["sta_width"] = m[2]


for key in devices.keys():
    fs = devices[key]
    if len(fs) > 1:
        bd = fs[0]["bus"] + ":" + fs[0]["device"]
        node = to_bd_node(fs[0])
        print('rectangle "{}" as {}'.format(bd, node) + " {")

    for f in fs:
        m = re.match(r'(.+?): (.+)', f["desc"])
        device_type = m[1]
        device_name = m[2]

        node = to_bdf_node(f)
        print('rectangle {} ['.format(node))
        print(f["bus"] + ":" + f["device"] + "." + f["func"] + " " + device_type)
        print(device_name)
        print(']')

        link(devices, f)

    if len(fs) > 1:
        print('}')

print("@enduml")
if args.markdown:
    print("```")