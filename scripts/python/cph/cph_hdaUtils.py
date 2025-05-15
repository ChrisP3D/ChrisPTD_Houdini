import hou

def setCurrentParmAsDefaultFromHDA(kwargs, parm:str):
    node = kwargs['node']
    newDefaultValue = node.parm(parm).eval()
    nodedef = node.type().definition()
    parmTemplateGroup = nodedef.parmTemplateGroup()

    p = parmTemplateGroup.find(parm)
    p.setDefaultValue((newDefaultValue,))
    
    parmTemplateGroup.replace(parmTemplateGroup.find(parm),p)

    nodedef.setParmTemplateGroup(parmTemplateGroup)
    
def getHDAbyNode(node):
    return HDA.node.type().definition()

def getHDAbyFile(file):
    return hou.hda.definitionsInFile(file)[0]


