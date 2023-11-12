import hou
import os
from cph import cph_sys

def writeDefaultProject(_hipfile_path):
    scripts_folder = cph_sys.getScriptsFolder()
    filepath_target = os.path.join(scripts_folder, '123.py')  
    _hipfile_path = _hipfile_path.replace("\\", "/")
    payload = f'hou.hipFile.merge("{_hipfile_path}")'

    with open(filepath_target, 'w') as file:
        file.write(payload)

def useCurrentHipCallback(result):
    if result:
        hipfile_path = hou.hipFile.path()
        writeDefaultProject(hipfile_path)
    hou.ui.displayMessage(f'Current Project Set as Default: {hipfile_path}')

def useSelectHipFileCallback(result):
    if result:
        file_path = hou.ui.selectFile()
        if file_path:
            hipfile_path = file_path
            writeDefaultProject(hipfile_path)
            hou.ui.displayMessage(f'Selected HIP from disk: {hipfile_path}')

def setDefaultProject():
    message = hou.ui.displayMessage("Choose an action:", buttons=("Use Current HIP as Default_", "Select HIP from Disk","Cancel"), close_choice= 2)

    # Handle the button clicks
    if message == 0:  # "Use Current HIP as Default"
        useCurrentHipCallback(True)
    elif message == 1:  # "Select HIP from Disk"
        useSelectHipFileCallback(True)


