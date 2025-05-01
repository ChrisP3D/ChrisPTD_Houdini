import hou
import weakref
from datetime import datetime
from time import gmtime, strftime
# Global dictionary to store callbacks

import inspect

def get_current_line():
    # Get the current frame
    frame = inspect.currentframe()
    # Get the caller's frame
    caller_frame = frame.f_back
    # Get the line number from the caller's frame
    line_number = caller_frame.f_lineno
    return line_number


# Call the function to initialize the session variables


###Utilities
#
#
#TODO FILTER FOR SURFACE NODES INSTEAD OF MATERIAL NETWORKS

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
#ADD


def initCallbacks(node):
    # cleanup_callbacks(node)
    node.removeAllEventCallbacks()
    node.addEventCallback((hou.nodeEventType.InputRewired,),onPreviewInputChanged)
    
# def cleanup_callbacks(node):
#     node.removeAllEventCallbacks()
    
#     for session_id, callback in list(hou.session.callback_registry.items()):
#         try:
#             node = hou.nodeBySessionId(session_id)
#             if node:
#                 node.removeEventCallback(callback)
#             del hou.session.callback_registry[session_id]
#         except hou.ObjectWasDeleted:
#             del hou.session.callback_registry[session_id]
#         except Exception as e:
#             print(f"Error cleaning up callback: {str(e)}")
#     hou.session.callback_registry.clear()

#Define Callback Events
def onPreviewInputChanged(node, event_type, **kwargs):
    """Calls convertPreviewInputsToTextureOps. Gets the node be"""
    convertPreviewInputsToTextureOps(node, bypass_prompt=True)

# def onInputDataChanged(node_id, **kwargs):
    
#     try:
#         # Try to get the node by its session ID
#         node = hou.nodeBySessionId(node_id)
        
#         if node is None:
#             print(f"Node with session ID {node_id} no longer exists or is invalid. Removing from Callback Registry")
#             if node_id in callback_registry:
#                 del callback_registry[node_id]
#             return
#         # hou.session.io_map[node]
#         # output = find_node_starting_with(node.parent(), 'suboutput')
#         # rewireOutput(output, -1)
        
#         # # print(f"Inputs rewired for node: {node.path()}")
#         sv = hou.ui.paneTabOfType(hou.paneTabType.SceneViewer)
#         sv.restartRenderer()
        
#         # Get the current time
#         # now = datetime.now()
        
#         # Print the current time including microseconds
#         print('hello')


#     except hou.ObjectWasDeleted:
#         print(f"Node with session ID {node_id} was deleted.")
#         # Remove the callback from our registry if the node no longer exists
#         if node_id in callback_registry:
#             del callback_registry[node_id]
#     except Exception as e:
#         print(f"Error in on_preview_inputs_changed for node with session ID {node_id}: {str(e)}")
#         import traceback
#         traceback.print_exc()

###Session Variables
#
#

def setSessionVariables(matnet, surface_op, disp_op, output_op):
    hou.session.matnet = matnet
    hou.session.surface_op = surface_op
    hou.session.disp_op = disp_op
    hou.session.output_op = output_op

def getSessionRefs():
    if hou.session.initialized:
        return hou.session.matnet, hou.session.surface_op, hou.session.disp_op, hou.session.output_op
# def setSessionVariables(matnet, surface_op, disp_op, output_op):
#     hou.session.matnet = weakref.ref(matnet)
#     hou.session.surface_op = weakref.ref(surface_op)
#     hou.session.disp_op = weakref.ref(disp_op)
#     hou.session.output_op = weakref.ref(output_op)

# def getSessionRefs():
#     if hou.session.initialized:
#         return (hou.session.matnet() if hou.session.matnet else None,
#                 hou.session.surface_op() if hou.session.surface_op else None,
#                 hou.session.disp_op() if hou.session.disp_op else None,
#                 hou.session.output_op() if hou.session.output_op else None)
        
def initSessionVars():
    
    if not hasattr(hou.session, 'initialized'):
        hou.session.initialized = True
    
    if not hasattr(hou.session, 'callback_registry'):
        hou.session.callback_registry = {}
    
    if not hasattr(hou.session, 'created_mtlx_nodes'):
        hou.session.created_mtlx_nodes = []
        
    if not hasattr(hou.session, 'io_map'):
        hou.session.io_map = {}

    #Ops
    if not hasattr(hou.session, 'matnet'):
        hou.session.matnet = None
    
    if not hasattr(hou.session, 'surface_op'):
        hou.session.surface_op = None
    
    if not hasattr(hou.session, 'disp_op'):
        hou.session.disp_op = None
    
    if not hasattr(hou.session, 'output_op'):
        hou.session.output_op = None
    


def refreshInput(node):
    pass
    
def rewireOutput(node, output_index = 0):
    output = node.outputs()[output_index]
    output.setInput(0,None)
    time.sleep(1)
    output.setInput(0,node)

def setInputNamesForRenderEngine(node, render_engine = 'karma'):
    if not hasattr(hou.session, 'io_map'):
        hou.session.io_map = {}

    cop_input_names = list(node.inputNames())
  
    if render_engine == 'karma':
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
    
    elif render_engine == 'redshift':
        pass
    elif render_engine == 'octane':
        pass
    elif render_engine == 'arnold':
        pass
    elif render_engine == 'vray':
        pass
    else:
        pass
    # Inits to None, populated every time a new mtlx image node is generated
    hou.session.io_map = {name: None for name in cop_input_names}
    
    return cop_input_names

def createMtlxNode(network, cop, datatype, input_name):
    """
    Creates a MaterialX (mtlx) image node in the specified network if it doesn't already exist, 
    and sets its parameters based on the provided datatype and cop node.

    Args:
        network (hou.Node): The Houdini node network where the new mtlximage node will be created.
        cop (hou.Node): The COP (Compositing) node used as the source for the image file path.
        datatype (str): The datatype of the image. Accepted values are 'Mono', 'RGB', 'RGBA', and 'Geometry'.
        input_name (str): The name to assign to the new mtlximage node. Each name is derived from the COP preview material input

    Returns:
        hou.Node: The created or existing mtlximage node.

    Notes:
        - If a node with the specified input_name already exists in the network, that node is returned.
        - The function keeps track of created nodes in hou.session.created_mtlx_nodes.
        - The function updates hou.session.io_map with the mapping from input_name to the created node.
        - The function sets the last created node and its state in hou.session.
        - If an unknown datatype is provided, a warning message is printed.
    """

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
    texture_op = network.createNode('mtlximage')
    texture_op.setName(input_name, unique_name=True)
    
    hou.session.io_map[input_name] = texture_op 
    
    hou.session.created_mtlx_nodes.append(texture_op)
    
    # Set parms
    if datatype in cop_signature_key:
        texture_op.parm('signature').set(cop_signature_key[datatype])
    else:
        print(f"Warning:createMtlxNode() Unknown datatype '{datatype}' for input '{input_name}'")
    
    texture_op.parm('file').set(f'op:{cop.path()}')
    
    texture_op.setSelected(1)
    texture_op.parent().layoutChildren()
    
    return texture_op

def removeEmptySurfaceInputs(preview_input_data, cop_input_names):
    """
    Removes unused MaterialX surface inputs from the Houdini session based on the provided COP input data and names.

    Args:
        cop_input_data (list): A list of dictionaries, each containing input data with a 'to_index' key representing the index of the COP input.
        cop_input_names (list): A list of strings representing the names of each input of the preview COP.

    Notes:
        - Named surface inputs are derived from the cop_input_data and cop_input_names. Should be passed from the output of setInputNamesForRenderEngine()
        - Nodes in hou.session.created_mtlx_nodes that are not listed in the named surface inputs are destroyed.
        - Special handling is applied to nodes with 'height' in their name to check and destroy related 'mtlxdisplacement' inputs.
        - The parent node's children are laid out after processing, if applicable.
        - The function updates hou.session.created_mtlx_nodes to only include the nodes that were kept.
    """
    """Cop input names are strings representing each input of the preview cop"""

    
    preview_input_names = [cop_input_names[input['to_index']] for input in preview_input_data]

    
    nodes_to_keep = []
    parent_node = None
    
    print(f'hou.session.created_mtlx_nodes : {hou.session.created_mtlx_nodes}')
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


            
            if node_name not in preview_input_names:
                print(f"Destroying node: {node_repr}")
                parent_node = node.parent()  # Store the parent before destroying the node
                
                if 'height' in node_name:
                    for input in output_op.inputs():
                        if 'mtlxdisplacement' in input.name():
                            input.destroy()
                else:
                    node.destroy()

            else:
                print(f"Keeping node: {node_repr}")
                nodes_to_keep.append(node)
                if parent_node is None:
                    parent_node = node.parent()  # Store the parent of a kept node

            node.parent().layoutChildren()
        except hou.ObjectWasDeleted:
            print(f"Node was deleted while checking: {node_repr}")
        except Exception as e:
            print(f"Unexpected error processing node {node_repr}: {str(e)}")

    hou.session.created_mtlx_nodes = nodes_to_keep
    
    

    
###Scripted UI
#
#
#TODO Refactor this to only search for surface vop nodes
def getMatNetDestination():
    """
    Prompts the user to select a Material X (Mtlx) destination through a custom confirmation dialog.

    The function presents a dialog with options to:
    - Update the previous Material X destination
    - Choose a Karma Material
    - Generate a new Material X node

    Based on the user's choice, the function performs the following:
    1. **Update Previous Destination**: Returns previously stored Material X nodes from `hou.session`, if available.
    2. **Choose Karma Material**: Allows the user to select a Material X node or generates a new one if no appropriate nodes are found.
    3. **Generate**: Creates and returns a new default Material X node.

    Returns:
        tuple: A tuple containing:
            - `matnet` (hou.Node): The Material X node (Material Network).
            - `surface_op` (hou.Node): The Material X surface operation node.
            - `disp_op` (hou.Node): The Material X displacement operation node.
            - `output_op` (hou.Node): The Material X output node.
        
        Returns `(None, None, None, None)` if the user cancels the operation.

    Raises:
        AttributeError: If there is an issue accessing `hou.session.previous`.
        hou.ObjectWasDeleted: If a node in `hou.session.previous` was deleted.
    """

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
                print(f"Warning: hou.sesion.previous is set to False")

        
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
            #TODO import generate function to create karmamat builder
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
def convertPreviewInputsToTextureOps(node, bypass_prompt=False):

    # Check if we should bypass the prompt
    if bypass_prompt and hou.session.previous:
        matnet, surface_node, disp_op, output_op = getSessionRefs()
        print(f"Exececuted{get_current_line()}")
        print(f'Session Refs: {getSessionRefs()}')
    else:
        matnet, surface_node, disp_op, output_op = getMatNetDestination()

    if matnet is None or surface_node is None or output_op is None:
        hou.ui.displayMessage('matnet is None or surface_node is None or output_op is None')
        return

    #convert the input string names to match the names of the input strings on the shader surface op
    cop_input_names = setInputNamesForRenderEngine(node)
    
    #Signatures
    cop_preview_input_data_types = node.inputDataTypes()
    idx_data_types = dict(enumerate(cop_preview_input_data_types))

    preview_input_data = node.inputsAsData()

    # Remove empty inputs first
    removeEmptySurfaceInputs(preview_input_data, cop_input_names)

    # Loop over Preview Material COP Input data
    input_cop = node.parent().node(preview_input_data[0]["from"])
    for input in preview_input_data:
        preview_input_index = input['to_index']
        input_cop_signature = idx_data_types[preview_input_index]

        # Geo
        if preview_input_index == 0:
            cop_sopimport = node.parent().node(input["from"])
            if cop_sopimport:
                geo_path = cop_sopimport.parm('soppath').evalAsString()

        ###Normal Map
        elif preview_input_index == 15:
            # Find existing normalmap node
            normalmap_mtlx_node = find_node_starting_with(matnet, 'mtlxnormalmap')
            
            if normalmap_mtlx_node is None:
                normalmap_mtlx_node = matnet.createNode('mtlxnormalmap')
                surface_node.setNamedInput('normal', normalmap_mtlx_node, 0)
            hou.session.created_mtlx_nodes.append(normalmap_mtlx_node)
            
            # Get or create the normal image node
            normal_texture_node = find_node_starting_with(matnet, 'normal')
            if normal_texture_node is None:
                normal_texture_node = createMtlxNode(matnet, input_cop, input_cop_signature, 'normal')
                #Override
                normal_texture_node.parm('signature').set('vector3')

            # Set the position of the normal image node to aid in layout
            normalmap_pos = normalmap_mtlx_node.position()
            normal_texture_node.setPosition((normalmap_pos[0] - 2, normalmap_pos[1]))

            # Connect the texture to the normal map 
            normalmap_mtlx_node.setInput(0, normal_texture_node)

            # Ensure normalmap is connected to the surface node
            if surface_node.input('normal') != normalmap_mtlx_node:
                surface_node.setNamedInput('normal', normalmap_mtlx_node, 0)


       ###Displacement
        elif preview_input_index == 16:
            displacement_texture_node = matnet.node('height') or createMtlxNode(matnet, input_cop, input_cop_signature, 'height')
            hou.session.created_mtlx_nodes.append(displacement_texture_node)


            disp_op = find_node_starting_with(matnet,"mtlxdisplacement") or matnet.createNode('mtlxdisplacement')
            hou.session.disp_op = disp_op
            
            # Connect nodes
            disp_op.setInput(0, displacement_texture_node)

            disp_input = next((i for i, input in enumerate(output_op.inputs()) if input and 'displacement' in input.name().lower()), None)
            if disp_input is not None:
                output_op.setInput(disp_input, disp_op)
            else:
                output_op.setInput(len(output_op.inputs()), disp_op)
            

        else:
            surf_input_name = cop_input_names[preview_input_index]
            texture_node = createMtlxNode(matnet, input_cop, input_cop_signature, surf_input_name)
            try:
                surface_node.setNamedInput(surf_input_name, texture_node, 0)
            except hou.InvalidInput:
                print(f'Warning: surf_input_name "{surf_input_name}" does not exist on the surface node')



###External Drivers
#
#
def main(node=None):

    try:
        initSessionVars()
        if node is None:
            if len(hou.selectedNodes()) == 1:
                node = hou.selectedNodes()[0]

        if node.type().name() != 'previewmaterial':
            hou.ui.displayMessage("Please select a Copernicus Preview Material node")
            return
    
        initCallbacks(node)

        # Check if the node already has a callback
        if len(node.eventCallbacks()) > 0:
            
            convertPreviewInputsToTextureOps(node, bypass_prompt=True)
        else:
            convertPreviewInputsToTextureOps(node, bypass_prompt=False)
    except Exception as e:
        hou.ui.displayMessage(f"An error occurred main(): {str(e)}")
    finally:
        # This ensures cleanup happens even if an error occurs
        # cleanup_callbacks(node)
        print('main.finally')
main()