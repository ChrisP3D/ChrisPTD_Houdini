import hou




def getCurrentNetworkEditorPane():
    editors = [pane for pane in hou.ui.currentPaneTabs() if isinstance(pane, hou.NetworkEditor) and pane.isCurrentTab()]
    return editors[-1]


def openParentParametersFloating():
    try:
        if getCurrentNetworkEditorPane().type() == hou.paneTabType.NetworkEditor:
            selectedNodes = hou.selectedNodes()
            if selectedNodes:
                selectedNode = selectedNodes[0]
                parent = selectedNode.parent()
                hou.ui.showFloatingParameterEditor(parent)
            else:
                hou.ui.displayMessage("Select a node to open its parent's Parameter Window")
        else:
            hou.ui.displayMessage("Current tab is not a Network Editor.")
    except IndexError:
        hou.ui.displayMessage("An IndexError occurred. Check if there are Network Editors and selected nodes.")



def openParentTypeProperties():
    """Open the Type Properties of the parent node of the selected node in the current network editor."""
    try:
        if getCurrentNetworkEditorPane().type() == hou.paneTabType.NetworkEditor:
            selectedNodes = hou.selectedNodes()
            if selectedNodes:
                selectedNode = selectedNodes[0]
                parent = selectedNode.parent()
                if parent.isUnlockedHDA:
                    hou.ui.openTypePropertiesDialog(parent.type())
            else:
                hou.ui.displayMessage("Select a node to open its parent's Type Properties")
        else:
            hou.ui.displayMessage("Current tab is not a Network Editor.")
    except IndexError:
        hou.ui.displayMessage("An IndexError occurred. Make sure a node is selected inside of a network editor.")

hou.ui.openParentTypeProperties = openParentTypeProperties
hou.ui.openParentParametersPane = openParentParametersFloating
