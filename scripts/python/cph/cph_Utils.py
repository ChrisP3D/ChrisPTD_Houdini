import hou

def getNodeDigits(node):
    """
    Extracts the digits from the node's name.
    Args:
        node (hou.Node): The node from which to extract digits.
    Returns:
        int: The extracted digits as an integer.
    """
    # Filter out non-digit characters and join the remaining digits
    return int(''.join(filter(str.isdigit, node.name())))

def findNetworkEditorPaneForNode(node):
    """
    Find the network editor pane for a given node.
    Args:
        node (hou.Node): The node for which to find the network editor pane.
    Returns:
        hou.NetworkEditor: The network editor pane containing the node, or None if not found.
    """
    # Get the parent network of the node
    parent_network = node.parent()
    
    # Iterate through all the pane tabs to find the network editor
    for pane in hou.ui.paneTabs():
        if isinstance(pane, hou.NetworkEditor):
            if pane.pwd() == parent_network:
                return pane
    return None

hou.Node.findNetworkEditorPaneForNode = findNetworkEditorPaneForNode