from cph import cph_NetworkUtils
import hou
import os



def createKarmaMatBuilder(destination_path,name='MaterialX Builder'):
    """Taken from user: CrisDoesCG at https://www.sidefx.com/forum/topic/95981/?page=1#post-422156
    Appended the functionality to add default nodes inside the network"""
    
    INHERIT_PARM_EXPRESSION = '''n = hou.pwd()
n_hasFlag = n.isMaterialFlagSet()
i = n.evalParm('inherit_ctrl')
r = 'none'
if i == 1 or (n_hasFlag and i == 2):
    r = 'inherit'
return r'''
    destination_node = hou.node(destination_path)
 
    subnetNode = destination_node.createNode("subnet",name)
    subnetNode.moveToGoodPosition()
    subnetNode.setMaterialFlag(True)                  
    
    parameters = subnetNode.parmTemplateGroup()

    newParm_hidingFolder = hou.FolderParmTemplate("mtlxBuilder","MaterialX Builder",folder_type=hou.folderType.Collapsible)
    control_parm_pt = hou.IntParmTemplate('inherit_ctrl','Inherit from Class', 
                        num_components=1, default_value=(2,), 
                        menu_items=(['0','1','2']),
                        menu_labels=(['Never','Always','Material Flag']))

    newParam_tabMenu = hou.StringParmTemplate("tabmenumask", "Tab Menu Mask", 1, default_value=["MaterialX parameter constant collect null genericshader subnet subnetconnector suboutput subinput"])
    class_path_pt = hou.properties.parmTemplate('vopui', 'shader_referencetype')
    class_path_pt.setLabel('Class Arc')
    class_path_pt.setDefaultExpressionLanguage((hou.scriptLanguage.Python,))
    class_path_pt.setDefaultExpression((INHERIT_PARM_EXPRESSION,))   

    ref_type_pt = hou.properties.parmTemplate('vopui', 'shader_baseprimpath')
    ref_type_pt.setDefaultValue(['/__class_mtl__/`$OS`'])
    ref_type_pt.setLabel('Class Prim Path')               

    newParm_hidingFolder.addParmTemplate(newParam_tabMenu)
    newParm_hidingFolder.addParmTemplate(control_parm_pt)  
    newParm_hidingFolder.addParmTemplate(class_path_pt)    
    newParm_hidingFolder.addParmTemplate(ref_type_pt)             

    parameters.append(newParm_hidingFolder)
    subnetNode.setParmTemplateGroup(parameters)
    
    props = subnetNode.createNode('kma_material_properties')
    surf = subnetNode.createNode('mtlxstandard_surface')
    disp = subnetNode.createNode('mtlxdisplacement')
    subnetNode.createNode('mtlxnormalmap')
    output = subnetNode.node('suboutput1')
    
    output.setInput(0, surf, 0)
    output.setInput(1, props, 0)
    output.setInput(2, disp, 0)

    subnetNode.layoutChildren()

    
    return subnetNode
def extractTexName(tex_path):
    tex_path = tex_path.split("_")
    return tex_path[-1].split('.jpg')[0]



#Windows
# debug_folders = ['H:/My Drive/Art/Roo/geo/Models/Environment/Desert/Foliage/Cactus_pot/',
#                  'H:/My Drive/Art/Roo/geo/Models/Environment/Desert/Foliage/DryBranches/',
#                  'H:/My Drive/Art/Roo/geo/Models/Environment/Desert/Cliff']




def selectStage():
    # Select LOPNET
    # Get all LOPNETS in the scene
    # If there are no LOPNETS, create one
    # If there are multiple, select one
    # If there is only one, use that one

    choices = []
    for child in hou.node('/obj').allSubChildren():
                if child.isNetwork():
                    if child.type() == hou.sopNodeTypeCategory().nodeType('lopnet') or child.type() == hou.objNodeTypeCategory().nodeType('lopnet'):
                        choices.append(child)
    choices.append(hou.node('/stage'))
    choice_strings = [c.path() for c in choices]
    selected_indices = hou.ui.selectFromList(
    choice_strings,
    title = "Select LOPNET",
    num_visible_rows=5,
    exclusive=True,
    default_choices=((0,))
    )
    if selected_indices is not None and len(selected_indices) == 1:
        lopnet = choices[selected_indices[0]]
    else:
        lopnet = choices[0]
    return lopnet
    


#Select Folder
def main():
    debug_folders = ['/Users/chrisp/Library/CloudStorage/GoogleDrive-pacificpatternsmusic@gmail.com/My Drive/Art/Roo/geo/Models/Environment/Desert/Cliff',
                    '/Users/chrisp/Library/CloudStorage/GoogleDrive-pacificpatternsmusic@gmail.com/My Drive/Art/Roo/geo/Models/Environment/Desert/Foliage/Cactus_pot',
                    '/Users/chrisp/Library/CloudStorage/GoogleDrive-pacificpatternsmusic@gmail.com/My Drive/Art/Roo/geo/Models/Environment/Desert/Foliage/DryBranches']


    export_paths = []

    debug = 0
    run = 0
    print(f'!!!DEBUG IS SET TO {debug}')


    if debug:
        folder_paths = debug_folders
        stage = hou.node('/stage')
    else:
        stage = selectStage()
        folder_paths = hou.ui.selectFile(
            title="Select Megascan Asset Folder",
            file_type=hou.fileType.Directory,
            multiple_select=True,
            default_value = None
        ).split(';')
       
        folder_paths = [hou.expandString(f.strip()) for f in folder_paths]

    if len(folder_paths) <= 1 and folder_paths[0] == '':
        hou.ui.displayMessage('No folder selected \n Rerun the shelf tool and select a folder')
        return

    #For each selected folder
    for folder in folder_paths:
        textures = []
        fbxs = []
        sops_imports = []
        asset_name = ''
        mat_paths = []
        rops = []
        
        #Create Sop Subnetwork
        sop_import_subnet = stage.createNode('subnet',"Sop_Imports")
        sop_merge = sop_import_subnet.createNode('merge')
        sopnet = sop_import_subnet.createNode('sopnet', 'sopnet1')
        sop_import_subnet.node('output0').setInput(0,sop_merge)

        #For each file in Folder
        for root, _, files in os.walk(folder, followlinks=False):
            #Gather Textures First
            for filename in files:
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff', '.tga', '.exr')):
                    if 'Billboard' not in filename:
                        textures.append(filename)
                elif filename.lower().endswith('.fbx'):

                    file_path = os.path.join(root, filename).replace("\\", "/")
                    asset_name = os.path.splitext(filename)[0]
                    print(f'127: {asset_name}')
                    fbxs.append(asset_name)

                    # Create File SOP
                    # filename without extension
                    folder_name = os.path.basename(root)

                    file_sop = sopnet.createNode('file', asset_name)
                    file_sop.parm('file').set(file_path)

                    #Sop Imports
                    sop_import = sop_import_subnet.createNode('sopimport', file_sop.name())

                    sop_import.parm('soppath').set(file_sop.path())
                    


        


        #Create Material

        print(f'146 : {asset_name}')
        
        matlib = stage.createNode('materiallibrary',f'matlib_{asset_name}')
        matlib.setInput(0,sop_import_subnet)
        matnet = createKarmaMatBuilder(matlib.path(),asset_name)


        assign_mat_node = stage.createNode('assignmaterial',f'assign_mats')

        assign_mat_node.setInput(0,matlib)
        assign_mat_node.parm('nummaterials').set(len(fbxs))

        
        for i,name in enumerate(fbxs):
            
            print(name)
            if name != '':

                assign_mat_node.parm(f'matspecpath{i}').set(f'/materials/{matnet.name()}')
                assign_mat_node.parm(f'primpattern{i}').set(f'/{name}')

        usd_rop = stage.createNode('usd_rop',asset_name)
        usd_rop.setInput(0,assign_mat_node)
        

        hip = hou.getenv('HIP')
        usd_rop.parm('lopoutput').set(f'{hip}/usd/{asset_name}.usd')
        export_paths.append(usd_rop.parm('lopoutput').eval())

        rops.append(usd_rop)
        #Wire Sop Imports in subnetwork
        for i, sop in enumerate(sop_import_subnet.children()):
            if sop.type() == sop_import.type():
                sop_merge.setInput(i,sop_import_subnet.children()[i])
        sop_import_subnet.layoutChildren()

        #Build Material Network
        surface_op = matnet.node('mtlxstandard_surface1')

        input_key = {}
        for i, name in enumerate(surface_op.inputNames()):
            input_key[name] = i

        #Generate Textures
        for t in textures:
            img_nodes = []

            tex_name = extractTexName(t)
            if tex_name == 'Bump' or tex_name =='Gloss':
                pass
            else:
                img = matnet.createNode('mtlximage', tex_name)
                img_nodes.append(img)
                img.parm('file').set(f'{folder}/{t}')
                
                #BaseColor AO and Cavity are multiplied later
                # basecolor = ao = cav = None #init as None 
                if tex_name == 'BaseColor':
                    basecolor = img
                    img_nodes.append(img)
                elif tex_name == 'AO':
                    ao = img
                    img_nodes.append(img)
                elif tex_name == 'Cavity':
                    cav = img
                    img_nodes.append(img)
                
                elif tex_name == 'Displacement':
                    img.parm('signature').set('defaut') #default is Float
                    mtlx_disp = matnet.node('mtlxdisplacement1')
                    mtlx_disp.setInput(0,img)

                elif tex_name == 'Normal':
                    img.parm('signature').set('vector3') 
                    mtlx_norm = matnet.node('mtlxnormalmap1')
                    mtlx_norm.setInput(0,img)
                    surface_op.setInput(input_key['normal'],mtlx_norm)
                
                elif tex_name == 'Specular':
                    img.parm('signature').set('defaut') 
                    surface_op.setInput(input_key['specular'],img)
                    
                elif tex_name == 'Roughness':
                    img.parm('signature').set('defaut') 
                    surface_op.setInput(input_key['specular_roughness'],img)
                    
                elif tex_name == 'Opacity':
                    img.parm('signature').set('defaut') 
                    surface_op.setInput(input_key['opacity'],img)
                
                elif tex_name == 'Translucency':
                    surface_op.setInput(input_key['transmission_color'],img)
                
        #Tint 
        
        tint = matnet.createNode('mtlxcolorcorrect', 'colorcorrect1')
        tint.setInput(0,basecolor)
        #Multiply AO Maps (only if basecolor, ao, and cav exist for this folder) 
        if basecolor and ao:
            mult_ao = matnet.createNode('mtlxmultiply','multiply_AO')
            mult_ao.setInput(0,tint)
            mult_ao.setInput(1,ao)
            if cav:
                mult_cav = matnet.createNode('mtlxmultiply','multiply_cav')
                mult_cav.setInput(0,mult_ao)
                mult_cav.setInput(1,cav)
                surface_op.setInput(input_key['base_color'],mult_cav)
            else:
                surface_op.setInput(input_key['base_color'],mult_ao)
        else:
            surface_op.setInput(input_key['base_color'], tint)
        
        tint_input_key = {}
        for i, name in enumerate(tint.inputNames()):
            tint_input_key[name] = i

        #Parameters
        # for input_name in tint.inputNames():
        #     if input_name != 'in':
        #         color_correct_parm = matnet.createNode('parameter',input_name)
        #         color_correct_parm.parm('parmname').set(input_name)
        #         color_correct_parm.parm('parmlabel').set(input_name.capitalize())
        #         color_correct_parm.parm('parmscope').set('subnet')
        #         tint.setInput(tint_input_key[input_name], color_correct_parm)



        for img in img_nodes:
            if len(img.outputs()) == 0:
                img.destroy()
                
        matnet.layoutChildren()

        #TODO popup to override current save
    hou.hipFile.save(hou.hipFile.path())


    #TODO add a scripted UI to allow user to choose they want to export as rops
    for rop in rops:
        rop.parm('executebackground').pressButton()
        

    stage.layoutChildren()   
    sopnet.layoutChildren()
    export_path_msg = '\n'.join(export_paths)

    hou.ui.displayMessage(f"""{len(export_paths)}Exported the following paths:
                          
                          {export_path_msg}""")



# print(f'Folder Paths : \n{folder_paths}\n')
# print(f'Folder Paths : \n{matnet_dict}\n')
# print(f'Folder Paths : \n{folder_textures}\n')