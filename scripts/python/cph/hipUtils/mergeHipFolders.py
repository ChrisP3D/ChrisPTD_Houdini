import os
import hou


#current_hip_path = hou.hipFile.path()
#hou.hipFile.merge(current_hip_path)

hip_extensions = (".hip", ".hiplc", ".hipnc", ".hipsc")

def extract_hip_name(file_path):
    path_without_extension = file_path.rsplit('.', 1)[0]
    hip_name = path_without_extension.rsplit('/', 1)[-1]
    return hip_name

def find_hip_files(folder_paths):
    hip_files = []
    
    if isinstance(folder_paths, str):
        folder_paths = [folder_paths]

    for folder in folder_paths:
        folder = folder.strip()
        for root, _, files in os.walk(folder):
            for filename in files:
                if filename.endswith(hip_extensions) and 'bak' not in filename:
                    file_path = os.path.join(root, filename)
                    if os.name == 'nt':  # Convert path for Windows
                        file_path = file_path.replace("\\", "/")
                    hip_files.append(file_path)
    
    return hip_files

def merge_hip_folders(folder_paths = None):
    #User selects directories
    if folder_paths is None:
        folder_paths = hou.ui.selectFile(
            file_type=hou.fileType.Directory,
            title="Select directories containing hip files",
            multiple_select=True
        )

    if folder_paths:
        # If the user selects multiple directories, split them into a list
        
        folder_paths = folder_paths.split(';')

        hip_files = find_hip_files(folder_paths)

        merged = []
        failed = []
        other = []
        
        #Merge
        for hip_file in hip_files:
            try:
                hou.ui.setStatusMessage(f"Merging file: {hip_file}")
                hou.hipFile.merge(hip_file)
                merged.append(hip_file)
                
            except Exception as e:
                hou.ui.setStatusMessage(f"Failed to merge file {hip_file}: {e}")
                failed.append(hip_file)
                

        for hip_file in hip_files:
            if hip_file not in merged and hip_file not in failed:
                other.append(hip_file)

        # Format the lists of files for a cleaner display
        merged_str = "\n  ".join(merged) if merged else "None"
        failed_str = "\n  ".join(failed) if failed else "None"
        other_str = "\n  ".join(other) if other else "None"

        # Display the message with formatted information
        hou.ui.setStatusMessage(f"""Successfully merged {len(merged)} files.
            Failed to merge {len(failed)} files.
            Succeeded:
            {merged_str}
            Failed:
            {failed_str}
            Other:
            {other_str}
            """)
    
    else:
        hou.ui.displayMessage("No directories selected.")



