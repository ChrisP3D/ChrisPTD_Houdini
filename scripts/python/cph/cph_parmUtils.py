# from cph import cph_parmUtils as pu

# pu.Dunderize()

import hou


def showInBrowser(parm):
    if isStringFileReference(parm):
        path = parm.evalAsString()
        hou.ui.showInFileBrowser(path)

def Dunderize(method='None'):
   
    methoddict = {'toggle': ToggleDunders,
               'insert': insertDunders,
               'remove': removeDunders,}
    
    skip_folder_names = ['Bindings']
    metachars = ['@',"^",'!']  
    
    for node in hou.selectedNodes():
        ptg = node.parmTemplateGroup()
        for parm in node.parms():
            if IsString(parm) and not isEditor(parm): 
                parmstring = getParmAsString(parm)
                if IsStringRegular(parm):
                    if not any(foldername in parm.containingFolders()[0] for foldername in skip_folder_names):
                        
                        methoddict[method](parm,metachars)
            
def convertParmStringToMultiParm(parm):

    parmval = getParmAsString(parm)
        
    spliters = ['/','.','#','ch',"chs",'"', "'",')',"(",'strcat',
                'ch("../")', "ch('../')",'chs("../")', "chs('../')",
                "#')",'#")',
                'detail(',
                'point(',
                'vertex(',
                'prim(','#']
    
    nums = [str(i) for i in range(10)]
    spliters += nums
    for s in spliters:
        if s in parmval:
            parmval = parmval.replace(s,"")
    
    if '#' in parmval:
        parmval = parmval.replace('#','')

    payload = f"ch(strcat('../{parmval}',detail(-1,'iteration',0)+1))"    
    parm.setExpression(payload)

def convertParmTupleToMultiParm(parmTup,scheme):
    
    if scheme == hou.parmNamingScheme.Base1:
        delimits = ['1','2','3','4']
    elif scheme == hou.parmNamingScheme.XYZW:
        delimits = ['x','y','z','w']
    elif scheme == hou.parmNamingScheme.RGBA:
        delimits = ['r','g','b','a']
    elif scheme == hou.parmNamingScheme.UVW:
        delimits = ['u','v','w']
    else:
        delimits = []
        
    for i, parm in enumerate(parmTup):
        parmval = getParmAsString(parm)
            
        spliters = ['/','.','#','ch',"chs",'"', "'",')',"(",'strcat',
                    'ch("../")', "ch('../')",'chs("../")', "chs('../')",
                    "#')",'#")',
                    'detail(',
                    'point(',
                    'vertex(',
                    'prim(','#']
        
        nums = [str(i) for i in range(10)]
        spliters += nums
        for s in spliters:
            if s in parmval:
                parmval = parmval.replace(s,"")
        for dl in delimits:
            if dl in parmval:
                parmval = parmval.replace(dl,"")
        
        
        if '#' in parmval:
            parmval = parmval.replace('#','')
        
        payload = f"ch(strcat(strcat('../{parmval}',detail(-1,'iteration',0)+1),{delimits[i]})"    
        parm.setExpression(payload)

def removeDunders(parm,metachars):
    pstr = getParmAsString(parm)
    
    if pstr == '*' or '':
        return

    if "__" in pstr: 
        forceSetParm(parm,pstr.replace("__",""))
        
def insertDunders(parm):
    metachars = ['@',"^",'!']  
    pstr = getParmAsString(parm)
    
    if pstr == '*' or '':
        return

    forceSetParm(parm,f"__{pstr}")
    
    if any(char in pstr for char in metachars):
        for mc in metachars:
            if mc in pstr:
                pstr = list(pstr)
                pstr.insert(pstr.index(mc)+1,"__")
        payload = "".join(pstr)
        forceSetParm(parm,payload)    

def ToggleDunders(parm):
    metachars = ['@',"^",'!']  
    parmstring = getParmAsString(parm)
        
    if "__" in parmstring: 
        forceSetParm(parm,parmstring.replace("__",""))

    elif parmstring == '*':
        pass
        
    else:
        forceSetParm(parm,f"__{parmstring}")
        
    if any(char in parmstring for char in metachars):
        if "__" in parmstring: 
            forceSetParm(parm,parmstring.replace("__",""))
            return
          
        for mc in metachars:
            if mc in parmstring:
                parmstring = list(parmstring)
                parmstring.insert(parmstring.index(mc)+1,"__")
            
        payload = "".join(parmstring)
        forceSetParm(parm,payload)        
        #     for split in splitstring:
        #         if mc in splitstring:
        #             split = list(split)
        #             split.insert(split.index(mc)+1, "__")
                    
        #             split = "".join(lpt)
        # forceSetParm(parm,payload)
                # if f"{mc}__" in parmstring or f"__{mc}" in parmstring:
                #     parmstring.replace(f"{mc}__", mc)
                #     parmstring.replace(f"__{mc}", mc)

    #             else:
    #                 payload = injectString(parmstring, mc, "__")
    #                 forceSetParm(parm,payload)
    #     else:
    #         for str in splitstring:
    #             str = f'__{str}'
    #         payload = " ".join(splitstring)
    #         forceSetParm(parm,payload)
    
    # else:
    #     for str in splitstring:
    #         str = f'__{str}'
    #     payload = " ".join(splitstring)
    #     forceSetParm(parm,payload)
        
        
    #_______________________
    # elif "@__" in parmstring:
    #     payload = parmstring.replace('@__',"@")
    #     forceSetParm(parm,payload)
        
    # # elif "@" in parmstring:
    # #     payload = parmstring.replace('@',"@__")

def convertParmStringAndAddInput(parm):
    print(f"Parm is type{type(parm)} of value {parm}")
    nodepath = getNodepathFromParm(parm)
    node = hou.node(nodepath)
    print(node)

    if len(getSpareParams(node)) > 0:
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

    payload = f"ch(strcat('../{name}',detail(-1,'iteration',0)+1))"    
    parm.setExpression(payload)


def createSpareInputParm(node):
    if not len(getSpareInputParams(node)):
        parmtemp = createSpareInputParmTemplate(0)
        parmtemp.setName("spare_input0")
    else:
        spare_ns = []
        for spare in getSpareInputParams(node):
            try:
                spare_ns.append(int(spare.path()[-1]))
            except NameError:
                pass
        parmtemp = createSpareInputParmTemplate(0)
        parmtemp.setName(f"spare_input{max(spare_ns)}")
    #if there is a parm with the name "spare_input0" reasigning the value to the found meta data node
        
    node.addSpareParmTuple(parmtemp)
    meta_relref = getNearestMetaNodeRelativePath(node)
    
    if meta_relref:
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

def getSpareInputParams(node):
    nspare_ins = []
    for p in node.parms():
        if p.isSpare():
            temp = p.parmTemplate()
            tags = list(temp.tags().keys())
            if 'cook_dependent' and 'opfilter' and 'oprelative' in tags:
                nspare_ins.append(p)
                
    return nspare_ins

def getFirstSpareInputParm(node):
    for p in node.parms():
        if p.isSpare():
            temp = p.parmTemplate()
            tags = list(temp.tags().keys())
            if 'cook_dependent' and 'opfilter' and 'oprelative' in tags:
                return p


def isSpare(parm):
    temp = parm.parmTemplate()
    tags = list(temp.tags().keys())
    if 'cook_dependent' and 'opfilter' and 'oprelative' in tags:
        return True

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

    if isinstance(node,list) or isinstance(node,tuple):
        selected_positions=[]
        for n in node:
            selected_positions.append(n.position())
    else:
        selected_positions = [node.position()]
    
    selected_positions = [node.position()]
    metanodes = []
    mn_dict = {}
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

def getSelectedParm():
    sel_node = hou.selectedNodes()[0]
    for parm in sel_node.parms():
        if parm.isShowingExpression():
            return parm
    
def isParmExpression(parm)->bool:
    return len(parm.keyframes()) >0
    
def getParmAsString(parm):
    if isParmExpression(parm):
        return str(parm.expression())
    else:
        return parm.evalAsString()
    
def forceSetParm(parm,_payload):
        if isParmExpression(parm):
            parm.setExpression(_payload)
        else:
            parm.set(_payload)

def injectString(string, key_char, injection):
    payload = ''
    idx = string.index(key_char)
    for i,char in enumerate(string):
            if i == idx:
                char += injection
            payload += char
            
    return payload
    


def getParmType(_parm):
    return _parm.parmTemplate().type()

def IsInt(parm)->bool:
    return parm.parmTemplate().type() == hou.parmTemplateType.Int
def IsFloat(parm)->bool:
    return parm.parmTemplate().type() == hou.parmTemplateType.Int
def IsString(parm)->bool:
    return parm.parmTemplate().type() == hou.parmTemplateType.String
def IsStringRegular(parm)->bool:
    return parm.parmTemplate().stringType() == hou.stringParmType.Regular
def isStringFileReference(parm)->bool:
    return parm.parmTemplate().stringType() == hou.stringParmType.FileReference

def hasTag(parm,tag)->bool:
    return str(tag) in list(parm.parmTemplate().tags().keys())

def isEditor(parm)->bool:
    return hasTag(parm,'editor')

def isGroup(parm):
    if 'group' in parm.name():
        return True
    
def convertAllParmsToMP(node):
    parms = node.parms()
    for parm in parms:
        if isParmExpression(parm):
            convertParmStringToMultiParm(parm)
    if not getNumSpareParams(node):
        createSpareInputParm(node)
        
    
    