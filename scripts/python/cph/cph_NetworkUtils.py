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
        for child in hou.node('/obj').allSubChildren():
            if child.isNetwork():
                if child.type() == hou.sopNodeTypeCategory().nodeType('lopnet') or child.type() == hou.objNodeTypeCategory().nodeType('lopnet'):
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
        new_sopimport.setName(node.name())
        #set parms
        new_sopimport.setParms({
                'soppath':node.path(),
                'asreference':1,})
                                
                                # 'adjustxformsforipnut':0,
                                # 'pathprefix':f"/{selectedNodes[0].parent().name()}",})

        new_sopimports.append(new_sopimport)
        
        
        if i <1:
            if len(sopimports) >0:
                connect_first = max(sopimports, key=cph_Utils.get_digits)
                new_sopimport.setInput(0,connect_first,0)
                new_sopimport.moveToGoodPosition()
                new_sopimport.setDisplayFlag(1)
        else:
            index = i-1
            new_sopimport.setInput(0,new_sopimports[index],0)
            new_sopimport.moveToGoodPosition()
            new_sopimport.setDisplayFlag(1)
            
    n_imported = len(selectedNodes)
    hou.ui.setStatusMessage(f'{n_imported} sopimports were added to "{lopnet.path()}"')


def updateNodesInNetwork(network,node_type,target_type):
    """Updates all nodes in a network"""
    for node in network.allSubChildren():
        if node.type() == node_type:
            node.changeNodeType(target_type)
def updateNodesInProject()

    hou.sopNodeTypeCategory().nodeType('filecache::2.0') 
    hou.sopNodeTypeCategory().nodeType('labs::filecache::2.0')


class NetworkTreeUtil():
    #hou.parm.unexpandedString()
    def __init__(self):
        self.file_cache_type = hou.sopNodeTypeCategory().nodeType('filecache::2.0') 
        self.labs_fc_type = hou.sopNodeTypeCategory().nodeType('labs::filecache::2.0')   
        
        self.storage = '$DCB'
        self.fasthdd = '$DCA'
        
        
        self.fcnodes = []
        self.fcbaseFolderParms = []
        
    def getAllFileCachesInProject(self,fc_type = 'all'):
        """_summary_

        Args:
            fc_type (str, optional): Defaults to 'all'. 'labs' retrieves only labs file cache, 'sidefx' retrieves sidefx file cache nodes
        """
        for child in hou.node('/').allSubChildren():
            if fc_type == 'all':
                if child.type() == self.file_cache_type or child.type() == self.labs_fc_type:
                    self.fcnodes.append(child)
            elif fc_type == 'labs':
                if child.type() == self.labs_fc_type:
                    self.fcnodes.append(child)
            elif fc_type == 'sidefx':
                if child.type() == self.file_cache_type:  
                    self.fcnodes.append(child)   
                    
                    
    def getAllNodesInProject(self,node_type):
        #get all file caches
        nodes = []
        for child in hou.node('/').allSubChildren():
            if child.type() == node_type:
                nodes.append(child)
        return nodes
                
    def getAllFileCacheBaseDirParms(self):
        for fc in self.fcnodes:
            self.fcbaseFolderParms.append(fc.parm('basedir'))
    
    def isExplicit(self,fcnode):
        return fcnode.parm('filemethod')      
      
    def forceFileConstructed(self,fcnode):
        if self.isExplict(fcnode):
            fcnode.parm('filemethod').set(0)
            
    def setBaseDirToStorage(self,fcnode):
        self.forceFileConstructed(fcnode)
        base_str = fcnode.parm('basedir').unexpandedString()
        self.swapString(base_str,self.fasthdd,self.storage)
        
        # def setBaseDirToFastHDD(self):
        #     self.forceFileConstructed(fcnode)
        #     base_str = fcnode.parm('basedir').unexpandedString()
        #     self.swapString(base_str,self.storage,self.fasthdd)
        #     #TODO
        #     #check dir, use os module to transfer file cache files to new folder
        
        folderpath = fcnode.parm('basedir').evalAsString()
        
    #TODO move to utils
    def swapString(self,string, swapout, swapin):
            string = list(string)
            string.insert(string.index(swapout)+1,swapin)
    
    #TODO
    # def setAllBaseDirsToStorage(self):
        
    # def setBaseDirToFastHDD(self):
        # pass
#TODO        
# def check_or_create_dir(directory_name):
#     """Create the directory if it doesn't exist"""
#     if not os.path.exists(directory_name):
#         os.makedirs(directory_name)
#         print(f"Directory '{directory_name}' created.")	
#     else:
#         #print('dir exists')
#         return
def convert_file_caches_to_labs(kwargs):
        
    me = kwargs['node']
    file_cache_type = hou.sopNodeTypeCategory().nodeType('filecache::2.0')
    labs_type = hou.sopNodeTypeCategory().nodeType('labs::filecache::2.0')
    
    scan_path = me.parm('opref_network_replace_labs_filecache').evalAsNodePath() 
    networkToScan = hou.node(scan_path)
    
    #get all file cache nodes and store in a list
    filecahces_to_convert = []

    for child in networkToScan.children():
        if child.type() == file_cache_type:
            filecahces_to_convert.append(child)
    
    new_labs_filecaches = []
    for fc in filecahces_to_convert:
        #get params

        filemethod = fc.parm('filemethod').eval()
        if filemethod == 1:
            file = fc.parm('file').unexpandedString()
        else:
            basename = fc.parm('basename').unexpandedString()
            filetype = fc.parm('filetype').eval()
            basedir = fc.parm('basedir').unexpandedString()
            enableversion = fc.parm('enableversion').eval()
            version = fc.parm('version').eval()
            
            
        timedependent = fc.parm('timedependent').eval()
        trange = fc.parm('trange').eval()
        cachesim = fc.parm('cachesim').eval()
        f1 = fc.parm('f1').eval()
        f2 = fc.parm('f2').eval()
        f3 = fc.parm('f3').eval()
        substeps = fc.parm('substeps').eval()
        loadfromdisk = fc.parm('loadfromdisk').eval()
        
        #get network
        pos = fc.position()
        input = fc.input(0)
        outputs = fc.outputs()
        
        #create new node
        labs_fc = networkToScan.createNode('labs::filecache::2.0')
        
        #set params
        labs_fc.parm('filemethod').set(filemethod)
        if filemethod == 1:
            labs_fc.parm('file').set(file)
        else:
            labs_fc.parm('basename').set(basename)
            labs_fc.parm('filetype').set(filetype)
            labs_fc.parm('basedir').set(basedir)
            labs_fc.parm('enableversion').set(enableversion)
            labs_fc.parm('version').set(version)
            
            
        labs_fc.parm('timedependent').set(timedependent)
        labs_fc.parm('trange').set(trange)
        labs_fc.parm('cachesim').set(cachesim)
        # labs_fc.parm('f1').deleteAllKeyframes()
        # labs_fc.parm('f2').deleteAllKeyframes()
        # labs_fc.parm('f3').deleteAllKeyframes()
        labs_fc.parm('f1').set(f1)
        labs_fc.parm('f2').set(f2)
        labs_fc.parm('f3').set(f3)
        labs_fc.parm('substeps').set(substeps)
        labs_fc.parm('loadfromdisk').set(loadfromdisk)
        
        
        #set network
        labs_fc.setPosition(pos)
        labs_fc.setInput(0,input)
        for output in outputs:
            output.setInput(0,labs_fc)

        
        new_labs_filecaches.append(labs_fc)

def getAveragePositionOfMultipleNodes(nodes):
    total_x = 0.0
    total_y = 0.0
    for node in nodes:
        pos = node.position()
        total_x += pos[0]
        total_y += pos[1]
    if len(nodes) > 0:
        avg_x = total_x / num_nodes
        avg_y = total_y / num_nodes
        return hou.Vector2(avg_x, avg_y)
    
def createKarmaMatBuilder(destination_path):
    """Taken from user: CrisDoesCG at https://www.sidefx.com/forum/topic/95981/?page=1#post-422156
    Appended the functionality to add default nodes inside the network"""
    
    INHERIT_PARM_EXPRESSION = '''n = hou.pwd()
n_hasFlag = n.isMaterialFlagSet()
i = n.evalParm('inherit_ctrl')
r = 'none'
if i == 1 or (n_hasFlag and i == 2):
    r = 'inherit'
return r'''
    destination_node = hou.node(destination_path)
 
    subnetNode = destination_node.createNode("subnet","karmamaterial")
    subnetNode.moveToGoodPosition()
    subnetNode.setMaterialFlag(True)                  
    
    parameters = subnetNode.parmTemplateGroup()

    newParm_hidingFolder = hou.FolderParmTemplate("mtlxBuilder","MaterialX Builder",folder_type=hou.folderType.Collapsible)
    control_parm_pt = hou.IntParmTemplate('inherit_ctrl','Inherit from Class', 
                        num_components=1, default_value=(2,), 
                        menu_items=(['0','1','2']),
                        menu_labels=(['Never','Always','Material Flag']))

    newParam_tabMenu = hou.StringParmTemplate("tabmenumask", "Tab Menu Mask", 1, default_value=["MaterialX parameter constant collect null genericshader subnet subnetconnector suboutput subinput"])
    class_path_pt = hou.properties.parmTemplate('vopui', 'shader_referencetype')
    class_path_pt.setLabel('Class Arc')
    class_path_pt.setDefaultExpressionLanguage((hou.scriptLanguage.Python,))
    class_path_pt.setDefaultExpression((INHERIT_PARM_EXPRESSION,))   

    ref_type_pt = hou.properties.parmTemplate('vopui', 'shader_baseprimpath')
    ref_type_pt.setDefaultValue(['/__class_mtl__/`$OS`'])
    ref_type_pt.setLabel('Class Prim Path')               

    newParm_hidingFolder.addParmTemplate(newParam_tabMenu)
    newParm_hidingFolder.addParmTemplate(control_parm_pt)  
    newParm_hidingFolder.addParmTemplate(class_path_pt)    
    newParm_hidingFolder.addParmTemplate(ref_type_pt)             

    parameters.append(newParm_hidingFolder)
    subnetNode.setParmTemplateGroup(parameters)
    
    props = subnetNode.createNode('kma_material_properties')
    surf = subnetNode.createNode('mtlxstandard_surface')
    disp = subnetNode.createNode('mtlxdisplacement')
    
    output = subnetNode.node('suboutput1')
    
    output.setInput(0, surf, 0)
    output.setInput(1, props, 0)
    output.setInput(2, disp, 0)

    for node in subnetNode.children():
        node.moveToGoodPosition()
    
    return subnetNode