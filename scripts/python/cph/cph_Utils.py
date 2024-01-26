import hou

def Test():
    print('This is my python module!')

def get_digits(node):
    return int(''.join(filter(str.isdigit, node.name())))

def getNodepathFromParm(parm):
    nodepath = parm.path().split(parm.name())[0]
    return nodepath

def getNodeRefFromParm(parm):
    nodepath = parm.path().split(parm.name())[0]
    
    return hou.node(nodepath)