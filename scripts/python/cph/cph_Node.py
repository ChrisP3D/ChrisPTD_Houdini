import hou

def isInsideLoop(node):
    #get nodes
    stream = []
    stream.append(node.inputAncestors())
    node.outputs
    #
    return bool

def getOutputsRecursive(node,outnodes,end=False):
    """Requires external list"""
    if not end:
        outputs = node.outputs()
        for out in outputs:
            if len(out.outputs())==0:
                outnodes.append(outnodes)
            
            else:
                getOutputsRecursive(out,outnodes,end= False,)