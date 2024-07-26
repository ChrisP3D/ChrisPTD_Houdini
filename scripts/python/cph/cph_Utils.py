import hou

def Test():
    print('This is my python module!')

def get_digits(node):
    return int(''.join(filter(str.isdigit, node.name())))

def findNetworkEditorPaneForNode(node):
    # Get the parent network of the node
    parent_network = node.parent()
    
    # Iterate through all the pane tabs to find the network editor
    for pane in hou.ui.paneTabs():
        if isinstance(pane, hou.NetworkEditor):
            if pane.pwd() == parent_network:
                return pane
    return None

hou.Node.findNetworkEditorPaneForNode = findNetworkEditorPaneForNode