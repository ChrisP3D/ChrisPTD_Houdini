import hou
import voptoolutils

def filterHasMatLibParent(node):
    if node.parent().type().name() == 'materiallibrary' or node.parent().type().name() == 'matnet':
        return True

def filterMtlxSurfaces(node):
    if node.type().name() == 'mtlxstandard_surface':
        return True

def createKarmaMatBuilder(destination_path):
    """Taken from CrisDoesCG at https://www.sidefx.com/forum/topic/95981/?page=1#post-422156
    Appended the functionality to add default nodes inside the network"""
    
    INHERIT_PARM_EXPRESSION = '''n = hou.pwd()
n_hasFlag = n.isMaterialFlagSet()
i = n.evalParm('inherit_ctrl')
r = 'none'
if i == 1 or (n_hasFlag and i == 2):
    r = 'inherit'
return r'''
    destination_node = hou.node(destination_path)
 
    subnetNode = destination_node.createNode("subnet","karmaMaterialBuilder")
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

def GetRenamedCopInputs(node):   
    cop_input_names = list(node.inputNames())
    
    # Manual renaming of preview mat cop
    for i in range(len(cop_input_names)):
        name = cop_input_names[i]
        if name == 'basecolor':
            name = 'base_color'
        elif name == 'spec_color':
            name = 'specular_color'
        elif name == 'roughness':
            name = 'specular_roughness'
        elif 'sss' in name:
            segs = name.split('sss')
            segs[0] = 'subsurface'
            name = ''.join(segs)
            if '_amount' in name:
                name = 'subsurface'
        cop_input_names[i] = name
    return cop_input_names

def createMtlxNode(karma_mat, cop, datatype, input_name):
    if not hasattr(hou.session, 'created_mtlx_nodes'):
        hou.session.created_mtlx_nodes = []

    cop_signature_key = {'Mono': 'default',
                         'RGB': 'color3',
                         'RGBA': 'color4',
                         'Geometry': None}        
    
    # Create Node
    mtlx_img = karma_mat.createNode('mtlximage')
    mtlx_img.setName(input_name, unique_name=True)
    
    hou.session.created_mtlx_nodes.append(mtlx_img)
    print(hou.session.created_mtlx_nodes)
    # Set parms
    mtlx_img.parm('signature').set(cop_signature_key[datatype])
    mtlx_img.parm('file').set(f'op:{cop.path()}')
    
    #TODO add callback to on deleted
    
    return mtlx_img


def GenerateMatAtDefault():
    matlib = hou.node('/stage/').createNode('materiallibrary')
    matnet = createKarmaMatBuilder(matlib.path())
    hou.ui.displayMessage(f'A New Material Library has been created at "/stage/{matlib}/karmaMatBuilder"')
    return matnet

def SetSessionVariables(matnet, surface_op, disp_op, output_op):
    hou.session.matnet = matnet
    hou.session.surface_op = surface_op
    hou.session.disp_op = disp_op
    hou.session.output_op = output_op
    hou.session.previous = True
    if not hasattr(hou.session, 'created_mtlx_nodes'):
        hou.session.created_mtlx_nodes = []
def GetMtlxDestination():
    if hasattr(hou.session, 'previous'):
        destination = hou.ui.displayCustomConfirmation("Pick a MaterialX Destination", buttons=('Update Previous Destination', 'Choose Karma Material', 'Generate', 'Cancel'), 
                                default_choice=0,
                                close_choice=-1,
                                help=None, title="Pick Destination")
    else:
        destination = hou.ui.displayCustomConfirmation("Pick a MaterialX Destination", buttons=('Choose Karma Material', 'Generate', 'Cancel'), 
                default_choice=0,
                close_choice=-1,
                help=None, title="Pick Destination")

    if destination == 3 or destination == -1:
        return None, None, None, None

    matnet = None
    surface_op = None
    disp_op = None
    output_op = None

    if destination == 0:
        try:
            if hou.session.previous:
                matnet = hou.session.matnet
                surface_op = hou.session.surface_op
                disp_op = hou.session.disp_op
                output_op = hou.session.output_op
                return matnet, surface_op, disp_op, output_op
        except AttributeError:
            destination = hou.ui.displayCustomConfirmation("No Previous Destination Found, please choose another option", buttons=('Choose Karma Material', 'Generate', 'Cancel'), 
                            default_choice=0,
                            close_choice=-1,
                            help=None, title="Pick Destination")
            if destination == 2 or destination == -1:
                return None, None, None, None
            destination += 1
        except hou.ObjectWasDeleted:
            destination = 1

    if destination == 1:
        found_matlibs = any(n.parent().type().name() in ['materiallibrary', 'matnet'] for n in hou.node('/').allSubChildren())
        
        if found_matlibs:
            matnet = hou.node(hou.ui.selectNode(custom_node_filter_callback=filterHasMatLibParent, title="Choose a Mtlx standard surface"))
            if matnet:
                surface_op = matnet.node('mtlxstandard_surface') or matnet.createNode('mtlxstandard_surface')
            else:
                return None, None, None, None
        else:
            matnet = GenerateMatAtDefault()
    elif destination == 2:
        matnet = GenerateMatAtDefault()

    if matnet:
        disp_op = matnet.node('mtlxdisplacement') or matnet.createNode('mtlxdisplacement')
        output_op = matnet.node('Material_Outputs_and_AOVs')
        SetSessionVariables(matnet, surface_op, disp_op, output_op)

    return matnet, surface_op, disp_op, output_op


def RemoveEmptySurfaceInputs(cop_input_data, cop_input_names, created_nodes):
    named_surf_inputs = []
    for input in cop_input_data:
        cop_input_index = input['to_index']
        named_surf_inputs.append(cop_input_names[cop_input_index])
    
    for node in hou.session.created_mtlx_nodes:
        if node.isValid() and node.name() not in named_surf_inputs:
            node.destroy()

                
def ConvertCopPreviewToMTLX(node,invoked_from='tool'):
    if invoked_from == 'menu':
        node = kwargs['node']
    if invoked_from == 'tool':
        node = hou.selectedNodes()[0]
    
    if node.type() != hou.nodeType(hou.copNodeTypeCategory(), 'previewmaterial'):
        hou.ui.displayMessage("Please Right Click a Copernicus Preview Material node")
        return
    
    matnet, surface_op, disp_op, output_op = GetMtlxDestination()
    if matnet is None or surface_op is None or disp_op is None or output_op is None:
        return

    cop_input_names = GetRenamedCopInputs(node)
    
    cop_preview_input_data_types = node.inputDataTypes()
    idx_data_types = dict(enumerate(cop_preview_input_data_types))
    
    cop_input_data = node.inputsAsData()

    hou.session.created_mtlx_nodes = []

    for input in cop_input_data:
        cop_input_index = input['to_index']
        cop = node.parent().node(input["from"])
        cop_signature = idx_data_types[cop_input_index]

        if cop_input_index == 0:
            cop_sopimport = node.parent().node(input["from"])
            geo_path = cop_sopimport.parm('soppath').evalAsString()
        elif cop_input_index == 15:    
            if 'normal' not in matnet.childrenAsData().keys():
                img_op = createMtlxNode(matnet, cop, cop_signature, 'normal')
                img_op.parm('signature').set('vector3')
                normal_op = matnet.createNode('mtlxnormalmap')
                normal_op.setInput(0, img_op)
                surface_op.setNamedInput('normal', normal_op, 0)
        elif cop_input_index == 16:    
            if 'height' not in matnet.childrenAsData().keys():
                img_op = createMtlxNode(matnet, cop, cop_signature, 'height')
                disp_op.setInput(0, img_op)
                if 'displacement' not in output_op.inputNames():
                    output_op.setInput(len(output_op.inputs()), disp_op)
        else:
            surf_input_name = cop_input_names[cop_input_index]
            if surf_input_name not in matnet.childrenAsData().keys():
                img_op = createMtlxNode(matnet, cop, cop_signature, surf_input_name)
                try:
                    surface_op.setNamedInput(surf_input_name, img_op, 0)
                except hou.InvalidInput:
                    hou.ui.displayMessage(f'surf_input_name is set to {surf_input_name}. Check the named input exists on the surface node')

    matnet.layoutChildren()
    try:
        RemoveEmptySurfaceInputs(cop_input_data, cop_input_names, hou.session.created_mtlx_nodes)
    except AttributeError:
        hou.session.created_mtlx_nodes = []

if len(hou.selectedNodes()):
    ConvertCopPreviewToMTLX('tool')


