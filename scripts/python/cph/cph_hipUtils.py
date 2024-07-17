import hou
import cph_sys




#hou.shelves.tool("name_of_tool") reference to shelf tool

def makeMergeHipScript():
    current_hippath = hou.hipFile.path()

    script = "import hou"
    script += "\n"
    script += "\n"
    script = f"{script}hou.hipFile.merge('{current_hippath}')"
    return script


https://www.sidefx.com/docs/houdini/hom/hou/hipFile.html#addEventCallback
https://www.sidefx.com/docs/houdini/hom/hou/hipFileEventType.html

def OpenMostRecentOnStartUp():
    scripts_folder = cph_sys.getScriptsFolder()
#Open most recent hip on start up
#Bind event to on close
    #Get hipfile path, save it to a json file the same folder as 123.py
    #Json object
    #{"MostRecent": "path to most recent hip",
    # "DoOpenRecent": 1}
    
#Create script inside same folder as 123.py
#edit 123.py to include script and run it