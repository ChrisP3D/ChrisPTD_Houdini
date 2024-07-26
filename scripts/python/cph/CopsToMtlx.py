import hou
import weakref

# Global dictionary to store callbacks
callback_registry = {}

###Utilities
#
#

def filterHasMatLibParent(node):
    if node.parent().type().name() == 'materiallibrary' or node.parent().type().name() == 'matnet':
        return True

def filterMtlxSurfaces(node):
    if node.type().name() == 'mtlxstandard_surface':
        return True
         
def find_node_starting_with(network, prefix):
    for node in network.children():
        if node.name().lower().startswith(prefix.lower()):
            return node
    return None



    
#Callbacks
#
#

def on_preview_inputs_changed(node_id, **kwargs):
    try:
        # Try to get the node by its session ID
        node = hou.nodeBySessionId(node_id)
        
        if node is None:
            print(f"Node with session ID {node_id} no longer exists or is invalid.")
            # Remove the callback from our registry if the node no longer exists
            if node_id in callback_registry:
                del callback_registry[node_id]
            return

        print(f"Inputs rewired for node: {node.path()}")
        convertCopPreviewToMTLX(node, bypass_prompt=True)
        update_text = f"MTLX network updated: {hou.time.strftime('%Y-%m-%d %H:%M:%S')}"

    except hou.ObjectWasDeleted:
        print(f"Node with session ID {node_id} was deleted.")
        # Remove the callback from our registry if the node no longer exists
        if node_id in callback_registry:
            del callback_registry[node_id]
    except Exception as e:
        print(f"Error in on_preview_inputs_changed for node with session ID {node_id}: {str(e)}")
        import traceback
        traceback.print_exc()

        
def add_preview_callback(preview_node):
    if preview_node.type().name() == 'previewmaterial':
        # Check if a callback already exists
        if preview_node.sessionId() in callback_registry:
            print(f"Callback already exists for node: {preview_node.path()}")
            return

        try:
            # Add event callback for InputRewired, passing the node's session ID
            callback = preview_node.addEventCallback((hou.nodeEventType.InputRewired,), 
                                                     lambda **kwargs: on_preview_inputs_changed(preview_node.sessionId(), **kwargs))
            if callback is not None:
                # Store the callback in our global registry
                callback_registry[preview_node.sessionId()] = callback
                print(f"Added callback for node: {preview_node.path()}")
            else:
                print(f"Warning: Could not add callback to {preview_node.path()}")
        except Exception as e:
            print(f"Error adding callback to {preview_node.path()}: {str(e)}")   
def remove_preview_callback(preview_node):
    if preview_node.type().name() == 'previewmaterial':
        try:
            callback = callback_registry.get(preview_node.sessionId())
            if callback:
                preview_node.removeEventCallback(callback)
                del callback_registry[preview_node.sessionId()]
                print(f"Removed callback for node: {preview_node.path()}")
            else:
                print(f"No callback found for node: {preview_node.path()}")
        except Exception as e:
            print(f"Error removing callback from {preview_node.path()}: {str(e)}")
def cleanup_callbacks():
    global callback_registry
    for session_id, callback in list(callback_registry.items()):
        try:
            node = hou.nodeBySessionId(session_id)
            if node:
                node.removeEventCallback(callback)
            del callback_registry[session_id]
        except hou.ObjectWasDeleted:
            del callback_registry[session_id]
        except Exception as e:
            print(f"Error cleaning up callback: {str(e)}")
    callback_registry.clear()
    
def getRenamedCopInputs(node):   
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

###Node Updates
#
#

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

def createMtlxNode(network, cop, datatype, input_name):
    if not hasattr(hou.session, 'created_mtlx_nodes'):
        hou.session.created_mtlx_nodes = []

    cop_signature_key = {
        'Mono': 'default',
        'RGB': 'color3',
        'RGBA': 'color4',
        'Geometry': None
    }

    # Check if a node with this name already exists
    existing_node = network.node(input_name)
    if existing_node:
        return existing_node

    # Create Node
    mtlx_img = network.createNode('mtlximage')
    mtlx_img.setName(input_name, unique_name=True)
    
    hou.session.created_mtlx_nodes.append(mtlx_img)
    hou.session.lastCreatedNode = mtlx_img
    hou.session.lastNodeState = 'create'
    
    # Set parms
    if datatype in cop_signature_key:
        mtlx_img.parm('signature').set(cop_signature_key[datatype])
    else:
        print(f"Warning: Unknown datatype '{datatype}' for input '{input_name}'")
    
    mtlx_img.parm('file').set(f'op:{cop.path()}')
    
    mtlx_img.setSelected(1)
    network.layoutChildren()
    return mtlx_img

def generateMatAtDefault():
    matlib = hou.node('/stage/').createNode('materiallibrary')
    matnet = createKarmaMatBuilder(matlib.path())
    hou.ui.displayMessage(f'A New Material Library has been created at "/stage/{matlib}/karmaMatBuilder"')
    return matnet

def removeEmptySurfaceInputs(cop_input_data, cop_input_names):
    print("Starting RemoveEmptySurfaceInputs")
    
    named_surf_inputs = [cop_input_names[input['to_index']] for input in cop_input_data]
    print(f"Named surface inputs: {named_surf_inputs}")
    
    nodes_to_keep = []
    parent_node = None

    for node in hou.session.created_mtlx_nodes:
        node_repr = f"Node of type {type(node)}"
        
        try:
            if node is None:
                print(f"Skipping node (None): {node_repr}")
                continue

            node_path = node.path()
            node_name = node.name()
            node_repr = f"Node '{node_name}' at {node_path}"
            
            if node.isInsideLockedHDA():
                print(f"Skipping node (inside locked HDA): {node_repr}")
                continue

            print(f"Checking node: {node_repr}")
            
            if node_name not in named_surf_inputs:
                print(f"Destroying node: {node_repr}")
                parent_node = node.parent()  # Store the parent before destroying the node
                node.destroy()
                hou.session.lastDestroyedNode = node
                hou.session.lastNodeState = 'destroy'
            else:
                print(f"Keeping node: {node_repr}")
                nodes_to_keep.append(node)
                if parent_node is None:
                    parent_node = node.parent()  # Store the parent of a kept node
        
        except hou.ObjectWasDeleted:
            print(f"Node was deleted while checking: {node_repr}")
        except Exception as e:
            print(f"Unexpected error processing node {node_repr}: {str(e)}")

    hou.session.created_mtlx_nodes = nodes_to_keep
    print(f"Number of nodes kept: {len(nodes_to_keep)}")

    # Layout children of the parent node if it exists
    if parent_node:
        try:
            parent_node.layoutChildren()
        except Exception as e:
            print(f"Error while laying out children: {str(e)}")

    print("Finished RemoveEmptySurfaceInputs")
    

###Session Variables
#
#

def setSessionVariables(matnet, surface_op, disp_op, output_op):
    hou.session.matnet = matnet
    hou.session.surface_op = surface_op
    hou.session.disp_op = disp_op
    hou.session.output_op = output_op
    hou.session.previous = True
    hou.session.lastNodeState = 'create'
    if not hasattr(hou.session, 'created_mtlx_nodes'):
        hou.session.created_mtlx_nodes = []

def getSessionRefs():
    if hou.session.previous:
        matnet = hou.session.matnet
        surface_op = hou.session.surface_op
        disp_op = hou.session.disp_op
        output_op = hou.session.output_op
        return matnet, surface_op, disp_op, output_op

###Scripted UI
#
#
def getMtlxDestination():
    matnet = surface_op = disp_op = output_op = None
    
    while True:
        if hasattr(hou.session, 'previous'):
            destination = hou.ui.displayCustomConfirmation(
                "Pick a Material X Destination", 
                buttons=('Update Previous Destination', 'Choose Karma Material', 'Generate', 'Cancel'),
                default_choice=0,
                close_choice=3,
                title="Pick Destination"
            )
        else:
            destination = hou.ui.displayCustomConfirmation(
                "", 
                buttons=('Choose Karma Material', 'Generate', 'Cancel'),
                default_choice=0,
                close_choice=2,
                title="Pick Destination"
            )
            destination += 1  # Adjust for the missing "Update Previous" option
        
        if destination in (3, -1):  # Cancel or close
            return None, None, None, None
        
        if destination == 0:  # Update Previous Destination
            try:
                if hou.session.previous:
                    return (hou.session.matnet, hou.session.surface_op, 
                            hou.session.disp_op, hou.session.output_op)
            except (AttributeError, hou.ObjectWasDeleted):
                hou.ui.displayMessage("No valid previous destination found. Please choose another option.")
                continue
        
        if destination == 1:  # Choose Karma Material
            found_matlibs = any(n.parent().type().name() in ['materiallibrary', 'matnet'] 
                                for n in hou.node('/').allSubChildren())
            if found_matlibs:
                matnet = hou.node(hou.ui.selectNode(
                    custom_node_filter_callback=filterHasMatLibParent, 
                    title="Choose a Mtlx standard surface"
                ))
                if not matnet:
                    continue
                surface_op = (find_node_starting_with(matnet, 'mtlxstandard_surface') or 
                              matnet.createNode('mtlxstandard_surface'))
            else:
                matnet = generateMatAtDefault()
        
        elif destination == 2:  # Generate
            matnet = generateMatAtDefault()
        
        if matnet:
            disp_op = (find_node_starting_with(matnet, 'mtlxdisplacement') or 
                       matnet.createNode('mtlxdisplacement'))
            output_op = matnet.node('Material_Outputs_and_AOVs')
            setSessionVariables(matnet, surface_op, disp_op, output_op)
            return matnet, surface_op, disp_op, output_op

###Main Script
#
#
           
def convertCopPreviewToMTLX(node, bypass_prompt=False):
    
    if node.type() != hou.nodeType(hou.copNodeTypeCategory(), 'previewmaterial'):
        hou.ui.displayMessage("Please Right Click a Copernicus Preview Material node")
        return

    # Check if we should bypass the prompt
    if bypass_prompt and hasattr(hou.session, 'previous') and hou.session.previous:
        matnet, surface_node, disp_op, output_op = getSessionRefs()
    else:
        matnet, surface_node, disp_op, output_op = getMtlxDestination()

    if matnet is None or surface_node is None or disp_op is None or output_op is None:
        return

    try:
        remove_preview_callback(node)
        if len(node.eventCallbacks())>0:
            node.removeAllEventCallbacks()
    except Exception as e:
        print(f"Error removing callback: {str(e)}")
    try:
        add_preview_callback(node)
    except Exception as e:
        print(f"Error adding callback: {str(e)}")

    cop_input_names = getRenamedCopInputs(node)
    
    #Used to cSignatures
    cop_preview_input_data_types = node.inputDataTypes()
    idx_data_types = dict(enumerate(cop_preview_input_data_types))

    cop_input_data = node.inputsAsData()

    if not hasattr(hou.session, 'created_mtlx_nodes'):
        hou.session.created_mtlx_nodes = []

    removeEmptySurfaceInputs(cop_input_data, cop_input_names)

    # For every wired input to Preview Material COP
    for input in cop_input_data:
        preview_cop_input_index = input['to_index']
        input_cop = node.parent().node(input["from"])
        input_cop_signature = idx_data_types[preview_cop_input_index]

        if not input_cop:
            continue

        # Geo
        if preview_cop_input_index == 0:
            cop_sopimport = node.parent().node(input["from"])
            if cop_sopimport:
                geo_path = cop_sopimport.parm('soppath').evalAsString()


        elif preview_cop_input_index == 15:
            # Find existing normalmap node
            normalmap_node = find_node_starting_with(matnet, 'mtlxnormalmap')
            
            if normalmap_node is None:
                normalmap_node = matnet.createNode('mtlxnormalmap')
                surface_node.setNamedInput('normal', normalmap_node, 0)

            # Get or create the normal image node
            normal_node = find_node_starting_with(matnet, 'normal')
            if normal_node is None:
                normal_node = createMtlxNode(matnet, input_cop, input_cop_signature, 'normal')
                normal_node.parm('signature').set('vector3')

            # Set the position of the normal image node
            normalmap_pos = normalmap_node.position()
            normal_node.setPosition((normalmap_pos[0] - 2, normalmap_pos[1]))

            # Connect the nodes
            normalmap_node.setInput(0, normal_node)
            matnet.layoutChildren()
            # Ensure normalmap is connected to the surface node
            if surface_node.input('normal') != normalmap_node:
                surface_node.setNamedInput('normal', normalmap_node, 0)
            matnet.layoutChildren()

                        


        # Displacement
        elif preview_cop_input_index == 16:
            if 'height' not in matnet.childrenAsData().keys():
                img_op = createMtlxNode(matnet, input_cop, input_cop_signature, 'height')
                disp_op.setInput(0, img_op)
                if 'displacement' not in output_op.inputNames():
                    output_op.setInput(len(output_op.inputs()), disp_op)
                    

        # Everything Else
        else:
            surf_input_name = cop_input_names[preview_cop_input_index]
            if surf_input_name not in matnet.childrenAsData().keys():
                img_op = createMtlxNode(matnet, input_cop, input_cop_signature, surf_input_name)
                try:
                    surface_node.setNamedInput(surf_input_name, img_op, 0)
                except hou.InvalidInput:
                    hou.ui.displayMessage(f'surf_input_name is set to {surf_input_name}. Check the named input exists on the surface node')

    
    try:
        removeEmptySurfaceInputs(cop_input_data, cop_input_names)
        matnet.layoutChildren() 
    except AttributeError:
        hou.session.created_mtlx_nodes = []
    add_preview_callback(node)





###External Drivers
#
#

def recreate_mtlx_network(preview_node):
    remove_preview_callback(preview_node)
    
    # Delete existing MTLX network
    matnet = getMtlxDestination()[0]
    if matnet:
        matnet.destroy()
    
    # Recreate the network
    convertCopPreviewToMTLX(preview_node)

def manual_update_mtlx(preview_node):
    remove_preview_callback(preview_node)
    try:
        convertCopPreviewToMTLX(preview_node)
    finally:
        add_preview_callback(preview_node)
        
def main(node=None):
    try:
        if node is None:
            if len(hou.selectedNodes()) == 1:
                node = hou.selectedNodes()[0]
            else:
                hou.ui.displayMessage("Please select a single Copernicus Preview Material node")
                return

        # Check if the node already has a callback
        if node.sessionId() in callback_registry:
            convertCopPreviewToMTLX(node, bypass_prompt=True)
        else:
            convertCopPreviewToMTLX(node, bypass_prompt=False)
    except Exception as e:
        hou.ui.displayMessage(f"An error occurred: {str(e)}")
    finally:
        # This ensures cleanup happens even if an error occurs
        cleanup_callbacks()

if __name__ == "__main__":
    main()
# main()
    
# Traceback (most recent call last):
# File "test", line 437, in <module>
# File "test", line 429, in main
# File "test", line 328, in ConvertCopPreviewToMTLX
# File "test", line 44, in remove_preview_callback
# NameError: name 'callback_registry' is not defined

# def create_custom_ui():
#     dialog = hou.ui.createDialog()
#     layout = dialog.mainLayout()
    
#     recreate_button = layout.createButton("Recreate MTLX Network")
#     update_button = layout.createButton("Manual Update MTLX")
    
#     def on_recreate():
#         node = hou.selectedNodes()[0]  # Assume a node is selected
#         recreate_mtlx_network(node)
    
#     def on_update():
#         node = hou.selectedNodes()[0]  # Assume a node is selected
#         manual_update_mtlx(node)
    
#     recreate_button.clicked.connect(on_recreate)
#     update_button.clicked.connect(on_update)
    
#     dialog.show()