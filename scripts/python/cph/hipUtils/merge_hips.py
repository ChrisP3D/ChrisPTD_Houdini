import os
import hou


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

def merge_hip_folders():
    #User selects directories
    selected_dirs = hou.ui.selectFile(
        file_type=hou.fileType.Directory,
        title="Select directories containing hip files",
        multiple_select=True
    )


    if selected_dirs:
        
        folder_paths = selected_dirs.split(';')

        hip_files = find_hip_files(folder_paths)

        merged = []
        failed = []
        other = []
        #Merge Operation
        
        for hip_file in hip_files:
            try:
                print(f"Merging file: {hip_file}")
                hou.hipFile.merge(hip_file)
                merged.append(hip_file)
                
            except Exception as e:
                print(f"Failed to merge file {hip_file}: {e}")
                failed.append(hip_file)
                

        for hip_file in hip_files:
            if hip_file not in merged and hip_file not in failed:
                other.append(hip_file)

        # Format the lists of files for a cleaner display
        merged_str = "\n  ".join(merged) if merged else "None"
        failed_str = "\n  ".join(failed) if failed else "None"
        other_str = "\n  ".join(other) if other else "None"

        # Display the message with formatted information
        hou.ui.displayMessage(f"""Successfully merged {len(merged)} files.
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
