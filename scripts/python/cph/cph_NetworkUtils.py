import hou
from cph import cph_Utils

def SelectedSopsToStage():
    """Creates a sopimport Lop with the selected nodes as a reference. 
    If a lopnet is one of the selected nodes, the sopimports will be created inside of the selected lopnet.
        If no lopnets are detected the sopimports will automatically be created in /stage"""
    
    selectedNodes = list(hou.selectedNodes())
    foundSelection = False
    for node in selectedNodes:
        if node.isNetwork():
            if node.type() == node.type() == hou.sopNodeTypeCategory().nodeType('lopnet') or node.type() == hou.objNodeTypeCategory().nodeType('lopnet'):
                lopnet = node
                foundSelection = True
                selectedNodes.remove(node)

    if not foundSelection:
        choices = []  
        for child in hou.node('/obj').children():
            if child.isNetwork():
                if node.type() == child.type() == hou.sopNodeTypeCategory().nodeType('lopnet') or child.type() == hou.objNodeTypeCategory().nodeType('lopnet'):
                    choices.append(child)
        choices.append(hou.node('/stage'))

        #two because /stage will always be added if nothing found in selection
        if len(choices) >= 2:
            choice_strings = [c.path() for c in choices]
            selected_indices = hou.ui.selectFromList(
                choice_strings,
                exclusive=True,
                default_choices=((0,))
            )
            if selected_indices is not None and len(selected_indices) == 1:
                lopnet = choices[selected_indices[0]]
        else:
            lopnet = choices[0]

    new_sopimports = []
    sopimports = []

    for node in lopnet.children():
        if node.type() == hou.lopNodeTypeCategory().nodeType('sopimport'):
            sopimports.append(node)
    for i,node in enumerate(selectedNodes):
        new_sopimport = lopnet.createNode('sopimport')

        #set parms
        new_sopimport.setParms({'soppath':node.path(),})
                                # 'asreferences':1,
                                # 'adjustxformsforipnut':0,
                                # 'pathprefix':f"/{selectedNodes[0].parent().name()}",})

        new_sopimports.append(new_sopimport)
        
        if i <1:
            if len(sopimports) >0:
                connect_first = max(sopimports, key=cph_Utils.get_digits)
                new_sopimport.setInput(0,connect_first,0)
                new_sopimport.moveToGoodPosition()
        else:
            index = i-1
            new_sopimport.setInput(0,new_sopimports[index],0)
            new_sopimport.moveToGoodPosition()

    n_imported = len(selectedNodes)
    if foundSelection:
        n_imported -= 1
    hou.ui.setStatusMessage(f'{n_imported} sopimports were added to "{lopnet.path()}"')


def findAndConnect(checklist,name, inputIndentifier,node):
    for i in checklist:
        i = name
        if i in checklist:
            node.setInput(RSinputKey[inputIndentifier], newNode,0)


def auto_material():
    import os    

    node = hou.pwd()

    geo = node.geometry()

    #the separator symbol inside of the filename
    separator = node.parm('separator').evalAsString()

    currentContext = node.parent()

    upperContext = currentContext.parent()

    children = currentContext.children()
    newNetName = node.parm('newNetName').evalAsString()
    newNetName.replace(" ", "_")
    #material network in which to add nodes
    contextEval = node.parm('material_context').evalAsString()

    if hou.node(contextEval) in children:
        parent = hou.node(contextEval)

    else:
        newMatNet = currentContext.createNode('matnet',newNetName)
        newMatPosition = (node.position().x() +2,node.position().y())
        newMatNet.setPosition(newMatPosition)
        newContext = node.setParms({'material_context': newMatNet.path()})
        
        parent = hou.node(newContext)


    #load texture files from folder
    parentfolder = node.parm('From_Parent_Folder').evalAsString()

    #TODO Update for material X
    #declair name constants and create other constant nodes
    rsTextureNode = "redshift::TextureSampler"
    rsMaterialNode = "redshift::Material"
    
    connectTo = parent.createNode(rsMaterialNode, "connectTo")
    displaceNode = parent.createNode("redshift::Displacement", "RsDisplacement")
    bumpNode = parent.createNode("redshift::BumpMap", "RsBumpMap")

    mainOutputNode = parent.createNode("redshift_material", "redshift_material_output")

    mainOutputNode.setInput(0,connectTo,0)
    mainOutputNode.setInput(1,displaceNode,0)
    mainOutputNode.setInput(2,bumpNode,0)

    #TODO Update to use regex
    diffuseList = ['Diffuse', 'diffuse','abledo']
    translucencyList = ['Translucency', 'translucency','TranslucencyColor']
    rehRoughList = ['ReflRoughness','Roughness']
    opacityList = ['opacity', 'Opacity', 'Transparency']

    needToConnect = [diffuseList, translucencyList, rehRoughList,opacityList]


    RSinputKey = {'diffuse': 0,
                'translucency': 3,
                'reflectionRoughness': 7,
                'opacity': 50,
                'translucencyWeight': 4}
                

#TODO make this function work on itson

    #Gather file paths into a list


    filepaths = []

    for root, dirs, files in os.walk(os.path.abspath(parentfolder)):
        for file in files:
            path = os.path.join(root, file)
            filepaths.append(path)
        
            
    #ExtractNames by separator parameter into a list
            
    filenames = []

    for file in filepaths:
        splitfile = file.split(separator)
        splitfilename = splitfile[-1]
        newname = splitfilename.split(".exr")[0]
        filenames.append(newname)

    newNodes = []

    for count, file in enumerate(filepaths):
        name = filenames[count]
        setpath = filepaths[count]
        
        newNode = parent.createNode(rsTextureNode, name)
        newNode.name = filenames[count]

        newName = newNode.name
        
        #TODO: find the other textures
        findAndConnect(diffuseList,newName,'diffuse', connectTo)    
        findAndConnect(translucencyList,newName,'translucency', connectTo)
        findAndConnect(opacityList,newName,'opacity',connectTo)
        
        if name == 'TranslucencyWeight':
            connectTo.setInput(4, newNode, 0)
        if name == 'Normal':
            bumpNode.setInput(0, newNode,0)
        if name == 'Displacement':
            displaceNode.setInput(0, newNode,0)  
        if name == 'ReflRoughness':
            connectTo.setInput(7,newNode,0)
            
        # set paths
        newNode.setParms({"tex0": filepaths[count]})
        newNodes.append(newNode)


    parent.layoutChildren()


