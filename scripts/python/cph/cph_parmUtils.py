import hou

def convertToMultiParm(parm):
    print(f"Parm is type{type(parm)} of value {parm}")
    nodepath = getNodepathFromParm(parm)
    node = hou.node(nodepath)
    print(node)

    if getNumSpareParams(node) > 0:
        spare_input_parm = getFirstSpareInputParm(node)
        if IsEmptyString(spare_input_parm):
            meta_relref = getNearestMetaNodeRelativePath(node)
            spare_input_parm.set(meta_relref)
    else:
        createSpareInputParm(node) #also references nearest metadata node
    
    
    expr = parm.expression()
    spliters = ['../','#','ch(','"', "'",')','strcat',
                'detail',
                'point',
                '']
    for s in spliters:
        name = expr.replace(s,"")
        print(name)
    payload = f"ch(strcat('../{name}',detail(-1,'iteration',0)+1))"    
    parm.setExpression(payload)
    

# ch(strcat("../bend",detail(-1,"iteration",0)+1))
def createSpareInputParm(node):
    inc_name_digit = getNumSpareParams(node)
    parmtemp = createSpareInputParmTemplate(0)
    parmtemp.setName("spare_input0")
    node.addSpareParmTuple(parmtemp)
    meta_relref = getNearestMetaNodeRelativePath(node)
    node.parm(parmtemp.name()).set(meta_relref)
    
def createSpareInputParmTemplate(digit):
    tags = { "cook_depend":"1",
            "opfilter" : "!!SOP!!",
            "oprelative" : "."}
    sptmp = hou.StringParmTemplate(
    name= f"spare_input0", 
    label=f"spareinput0", 
    num_components = 1,
    tags = tags,
    string_type= hou.stringParmType.NodeReference
    )
    return sptmp

def getNumSpareParams(node):
    nspares = 0
    for p in node.parms():
        if p.isSpare():
            temp = p.parmTemplate()
            tags = list(temp.tags().keys())
            if 'cook_dependent' and 'opfilter' and 'oprelative' in tags:
                nspares += 1
                
    return nspares

def getFirstSpareInputParm(node):
    for p in node.parms():
        if p.isSpare():
            temp = p.parmTemplate()
            tags = list(temp.tags().keys())
            if 'cook_dependent' and 'opfilter' and 'oprelative' in tags:
                return p



def IsEmptyString(parm):
    if parm.evalAsString() == '':
        return True

def getNodepathFromParm(parm):
    nodepath = parm.path().split(parm.name())[0]
    return nodepath

def getNodeRefFromParm(parm):
    nodepath = parm.path().split(parm.name())[0]
    
    return hou.node(nodepath)

def getNearestMetaNodeRelativePath(node):
    metanodes = []
    min_dists = []
    for n in node.parent().children():
        if n.type() == hou.sopNodeTypeCategory().nodeType('block_begin'):
            if n.parm('method').eval() == 2:  # Metadata setting
                metanodes.append(n)
                mn_dict[n] = {'pos': n.position(), 'dist': []}
    for mn in mn_dict:
        for nodepos in selected_positions:
            dist = nodepos.distanceTo(mn_dict[mn]['pos'])
            mn_dict[mn]['dist'].append(dist)  # Append the distance to the list

    mindist = min(dist for mn in mn_dict for dist in mn_dict[mn]['dist'])

    closest_mn = [mn for mn in mn_dict if mindist in mn_dict[mn]['dist']][0]
    
    return f"../{closest_mn.name()}"

    
sel_nodes = hou.selectedNodes()
selected_positions = [node.position() for node in sel_nodes]

metanodes = []
mn_dict = {}
for node in sel_nodes[0].parent().children():
    if node.type() == hou.sopNodeTypeCategory().nodeType('block_begin'):
        if node.parm('method').eval() == 2:  # Metadata setting
            metanodes.append(node)
            mn_dict[node] = {'pos': node.position(), 'dist': []}

for mn in mn_dict:
    for nodepos in selected_positions:
        dist = nodepos.distanceTo(mn_dict[mn]['pos'])
        mn_dict[mn]['dist'].append(dist)  # Append the distance to the list

mindist = min(dist for mn in mn_dict for dist in mn_dict[mn]['dist'])

closest_mn = [mn for mn in mn_dict if mindist in mn_dict[mn]['dist']][0]


target = f"../{closest_mn.name()}"
tags = { "cook_depend":"1",
            "opfilter" : "!!SOP!!",
            "oprelative" : "."}
    

# Create a String parameter template
sptmp = hou.StringParmTemplate(
    name="spareInput1", 
    label="spareinput1", 
    num_components = 1,
    tags = tags,
    string_type= hou.stringParmType.NodeReference
    )




spareparms_dict = {}
for node in sel_nodes:
    spareparms_dict[node] = {
        'spareparm_list': [],
        'parmTemp': sptmp,
        'created_parm_name':''
    }
    
    # Iterate over parameters to find existing spare parameters
    for p in node.parms():
        if p.isSpare():
            spare_name = p.name()
            spareparms_dict[node]['spareparm_list'].append(spare_name)
    
    # Find the maximum digit in existing spare parameter names
    max_digit = max(
        [int(''.join(filter(str.isdigit, name))) for name in spareparms_dict[node]['spareparm_list']],
        default=0
    )
    
    # Set a new name for the spare parameter based on max_digit
    new_spare_name = f'spareInput{max_digit + 1}'
    
    #Parm Template attribute name update
    spareparms_dict[node]['parmTemp'].setName(new_spare_name)
    
    # Create the spare parameter
    node.addSpareParmTuple(spareparms_dict[node]['parmTemp'])
    node.parm(spareparms_dict[node]['parmTemp'].name()).set(target)
