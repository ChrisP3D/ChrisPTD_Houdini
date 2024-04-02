import hou
import os
import tempfile
from cph import cph_sys, cph_Utils

def writeDefaultProject(_hipfile_path, write = 1):
    scripts_folder = cph_sys.getScriptsFolder()
    filepath_target = os.path.join(scripts_folder, '123.py')  
    _hipfile_path = _hipfile_path.replace("\\", "/")
    payload = f'\nhou.hipFile.merge("{_hipfile_path}")'
    if write:
        with open(filepath_target, 'w') as file:
            file.write(payload)
    return payload

def useCurrentHipCallback():
    hipfile_path = hou.hipFile.path()
    writeDefaultProject(hipfile_path)
    hou.ui.displayMessage(f'Current Project Set as Default: {hipfile_path}')

def useSelectHipFileCallback():
    file_path = hou.ui.selectFile()
    if file_path:
        hipfile_path = hou.text.expandString(file_path)
        writeDefaultProject(hipfile_path)
        hou.ui.displayMessage(f'Selected HIP from disk: {hipfile_path}')

def setDefaultHip(message):
    if message == 0:
            if hou.hipFile.isNewFile():
                saveprompt = hou.ui.displayMessage("Hip Must Be Saved First!", buttons=("Save","Cancel"), close_choice= 1)
                if saveprompt == 1:
                    return
                if saveprompt == 0:
                    savefile_path = hou.ui.selectFile()
                    if savefile_path:
                        hou.hipFile.save(savefile_path)
                    else:
                        return
            hipfile_path = hou.hipFile.path()
            writeDefaultProject(hipfile_path)
            hou.ui.displayMessage(f'Current Project Set as Default: {hipfile_path}')
            
            
    if message == 1:
        file_path = hou.ui.selectFile()
        if file_path:
            hipfile_path = hou.text.expandString(file_path)
            writeDefaultProject(hipfile_path)
            hou.ui.displayMessage(f'Selected HIP from disk: {hipfile_path}')


    if message == 2:
        hou.ui.displayConfirmation('Coming soon! For now you must remove the line containing "hou.hipfile.merge(filepath to start up hip contents)"\nfrom the startup script located at $HOUDINI_USER_PREF_DIR/scripts/123.py\nIMPORTART!!! \n If the file is empty houdini will not open',
                                severity = hou.severityType.Error)
    #TODO
    #     scripts_folder = cph_sys.getScriptsFolder()
    #     scriptfile = os.path.join(scripts_folder, '123.py')  
    #     scriptfile = scriptfile.replace("\\", "/")
        
    #     remove_text = 'hou.hipFile.merge'
        
    #     temp_fd, temp_path = tempfile.mkstemp()
        
    #     with open(scriptfile,'r') as file, os.fdopen(temp_fd, 'w') as temp_file:
    #         for line in file:
    #             if remove_text in line:
    #                 temp_file.write(line)

    #     hou.hipFile.addEventCallback()
    #     os.replace(temp_path, scriptfile)


def setDefaultProject():
    message = hou.ui.displayMessage("Choose an action:", buttons=("Use Current HIP as Default_", "Select HIP from Disk","Clear and Reset to default","Cancel"), close_choice= 3)

    setDefaultHip(message)

