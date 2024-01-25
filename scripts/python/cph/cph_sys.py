import os
import hou
import sys

def localDirToScanPath(dir_name):
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    tools_dir = os.path.join(cur_dir, 'cph_tools')

    # Add the directory to the sys.path list temporarily
    sys.path.insert(0, tools_dir)

def check_or_create_dir(directory_name):
    """Create the directory if it doesn't exist"""
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)
        print(f"Directory '{directory_name}' created.")	
    else:
        #print('dir exists')
        return

def getScriptsFolder():
    """Returns scripts directory path from HOUDINI_USER_PREF_DIR"""
    scripts_folder = os.path.join(hou.getenv('HOUDINI_USER_PREF_DIR'),'scripts')
    check_or_create_dir(scripts_folder)

    return scripts_folder

def Test():
    print("cph_sys exists")
