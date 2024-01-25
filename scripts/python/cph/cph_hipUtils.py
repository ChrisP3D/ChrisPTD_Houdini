import hou


#hou.shelves.tool("name_of_tool") reference to shelf tool

def makeMergeHipScript():
    current_hippath = hou.hipFile.path()

    script = "import hou"
    script += "\n"
    script += "\n"
    script = f"{script}hou.hipFile.merge('{current_hippath}')"
    return script

    