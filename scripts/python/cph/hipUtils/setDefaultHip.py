import hou
import os
from cph import cph_sys

def writeDefaultProject(hipfile_path, write = 1):
    scripts_folder = cph_sys.getScriptsFolder()
    filepath_target = os.path.join(scripts_folder, '123.py')  
    hipfile_path = hipfile_path.replace("\\", "/")
    payload = f'\nhou.hipFile.merge("{hipfile_path}")'
    if write:
        with open(filepath_target, 'w') as file:
            file.write(payload)
    return payload

def resetDefaultProject():
    filepath_target = os.path.join(cph_sys.getScriptsFolder(), '123.py') 
    with open(filepath_target, 'r') as file:
        lines = file.readlines()
    # Remove lines that start with "hou.hipFile.merge"
    lines = [line for line in lines if not line.lstrip().startswith("hou.hipFile.merge")]
    with open(filepath_target, 'w') as file:
        file.writelines(lines)
    
def useCurrentHip():
    hipfile_path = hou.hipFile.path()
    writeDefaultProject(hipfile_path)
    hou.ui.displayMessage(f'Current Project Set as Default: {hipfile_path}')

def useSelectHipFile():
    file_path = hou.ui.selectFile()
    if file_path:
        hipfile_path = hou.text.expandString(file_path)
        writeDefaultProject(hipfile_path)
        hou.ui.displayMessage(f'Selected HIP from disk: {hipfile_path}')

def setDefaultHip(message):
    #Use current hip as default
    if message == 0:
        if hou.hipFile.isNewFile():
            saveprompt = hou.ui.displayMessage("Hip Must Be Saved First!", buttons=("Save","Cancel"), close_choice= 1)
            #cancel
            if saveprompt == 1:
                return
            #save
            if saveprompt == 0:
                savefile_path = hou.ui.selectFile()
                if savefile_path:
                    hou.hipFile.save(savefile_path)
                else:
                    return
        hipfile_path = hou.hipFile.path()
        writeDefaultProject(hipfile_path)
        hou.ui.displayMessage(f'Current Project Set as Default: {hipfile_path}')
            
    #Select HIP from disk       
    if message == 1:
        file_path = hou.ui.selectFile()
        if file_path:
            hipfile_path = hou.text.expandString(file_path)
            writeDefaultProject(hipfile_path)
            hou.ui.displayMessage(f'Selected HIP from disk: {hipfile_path}')


    if message == 2:
        if hou.ui.displayConfirmation('Reset start up hip to default settings?'):
            resetDefaultProject()
            hou.ui.setStatusMessage('Reset to default settings')

def setDefaultHipPrompt():
    message = hou.ui.displayMessage("Choose an action:", buttons=("Use Current HIP as Default_", "Select HIP from Disk","Clear and Reset to default","Cancel"), close_choice= 3)
    if message == 3:
        return
    else:
        setDefaultHip(message)  

