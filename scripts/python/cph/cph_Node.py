import hou

def isInsideLoop(node,levels=1):
    #get nodes

    input_ancestors = node.inputAncestors()
    begin_type = hou.sopNodeTypeCategory().nodeType('block_begin')


    #if first input is block begin return 
    if input_ancestors[0].type() == begin_type():
        return True

    #get all input types
    input_ancestors_input_types = []
    for input in input_ancestors_input_types:
        if input.type() == begin_type or input.type() == end_type:
            input_ancestors_input_types.append(input)

    #check if any inputs at all are input blocks
    checkfor_set = set(begin_type)
    inputtypes_set = set(input_ancestors_input_types)
    if len(checkfor_set.intersection(inputtypes_set))==0:
        return False


    begin_block_dict = {'index':0}
    for i, node in enumerate(input_ancestors):
        begin_block_dict[node] = {'index':-1,'name':node.name()}
        if node.type() == begin_type or node.type() == end_type:
            begin_block_dict[node]['index'] = i
            begin_block_dict[node]['name'] = node.name()

    #get first occurence
    first_begin_block = min(node for node in begin_block_dict for node in begin_block_dict[node]['index'])
    


    outnodes = node.outputs()
    end_type = 'block_end'
    allouts = getOutputsRecursive(node=node, outnodes=outnodes,curiter=0,maxiter=10,stop_on_type=end_type)

    #try probably found the first block begin instance
    if len(allouts) == 1:
        return True
    
    
    #
    return bool

def getOutputsRecursive(node,outnodes,curiter,maxiter=50,stop_on_type = ''):
    #check stop type if string provided
    if len(stop_on_type):
        if node.type() == hou.node(stop_on_type).type():
            return node
    
    iter = curiter

    if iter == maxiter:
        return outnodes
    else:
        iter +=1

    for node in outnodes:
        if len(node.outputs()) == 0:
            return outnodes
        else:
            for outnode in node.outputs():
                outnodes.append(outnode)
                getOutputsRecursive(node = outnode, outnodes = outnode.outputs(),curiter=iter,stop_on_type=stop_on_type)

def getInputsRecursive(node,in_nodes,curiter,maxiter=50,stop_on_type = ''):
    if len(stop_on_type):
        if node.type() == hou.node(stop_on_type).type():
            return in_nodes
    iter = curiter

    if iter == maxiter:
        return in_nodes
    else:
        iter +=1
    for node in in_nodes:
        if len(node.inputs()) == 0:
            return in_nodes
        else:
            for input in node.inputs():
                in_nodes.append(input)
                getOutputsRecursive(node = input, in_nodes = input.inputs(),curiter=iter,stop_on_type=stop_on_type)
    
