import hou

def setCurrentParmAsDefaultFromHDA(kwargs, parm_name:str):
    """_summary_ 

    Args:
        parm_name (str): The string representing the name of the parameter to update
    """
    node = kwargs['node']
    newDefaultValue = node.parm(parm_name).eval()
    nodedef = node.type().definition()
    parmTemplateGroup = nodedef.parmTemplateGroup()

    p = parmTemplateGroup.find(parm_name)
    p.setDefaultValue((newDefaultValue,))
    
    parmTemplateGroup.replace(parmTemplateGroup.find(parm_name),p)

    nodedef.setParmTemplateGroup(parmTemplateGroup)

def updateHipDict(kwargs):
    
    me = kwargs['node']
    hipdict = me.parm('dct_hipfiles')

    name = hou.hipFile.name()
    path = hou.hipFile.path()
    hipdict.set({name:path})
def test2():
    print('hello')
    

def getHDAbyNode(node):
    return HDA.node.type().definition()

def getHDAbyFile(file):
    return hou.hda.definitionsInFile(file)[0]


