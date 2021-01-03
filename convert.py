import sys
import re

def to_bd_node(f):
    return "node" + f["bus"] + "_" + f["device"]

def to_bdf_node(f):
    return "node" + f["bus"] + "_" + f["device"] + "_" + f["func"]

def link(funcs, current, aggregate):
    bus = int(current["bus"], 16)
    for key in funcs.keys():
        fs = funcs[key]
        for f in fs:
            if f["is_pci_bridge"]:
                if f["child_from"] <= bus and bus <= f["child_to"]:
                    if aggregate:
                        print('{} --> {}'.format(to_bdf_node(f), to_bd_node(current)))
                    else:
                        print('{} --> {}'.format(to_bdf_node(f), to_bdf_node(current)))

is_pci_bridge = False

print("```plantuml")
print("@startuml")

print("left to right direction")
print("rectangle root")

funcs = {}
current = None
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
        if funcs.get(bd):
            funcs[bd].append(f)
        else:
            funcs[bd] = [f]

        current = f
    else:
        if is_pci_bridge:
            m = re.match(r'\s+Bus: primary=([\da-f]+), secondary=([\da-f]+), subordinate=([\da-f]+)', l)

            if m:
                current["child_from"] = int(m[2], 16)
                current["child_to"] = int(m[3], 16)

for key in funcs.keys():
    fs = funcs[key]
    if len(fs) > 1:
        bd = fs[0]["bus"] + ":" + fs[0]["device"]
        node = to_bd_node(fs[0])
        if fs[0]["bus"] == "00":
            print('root --> {}'.format(node))
        else:
            link(funcs, fs[0], True)
        print('rectangle "{}" as {}'.format(bd, node) + " {")

    for f in fs:
        m = re.match(r'(.+?): (.+)', f["desc"])
        device_type = m[1]
        device_name = m[2]

        node = to_bdf_node(f)
        print('rectangle {} ['.format(node))
        print(f["bus"] + ":" + f["device"] + "." + f["func"])
        print(device_type)
        print(device_name)
        print(']')

        if len(fs) == 1:
            if f["bus"] == "00":
                print('root --> {}'.format(node))
            else:
                link(funcs, f, False)

    if len(fs) > 1:
        print('}')

print("@enduml")
print("```")