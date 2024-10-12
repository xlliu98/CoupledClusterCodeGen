from Classes import *
from math import factorial
from fractions import Fraction
from copy import deepcopy

sign = lambda a: (a>0) - (a<0)
def commutator(operatorStrList1, operatorStrList2):
    return operatorStrList1 * operatorStrList2 - operatorStrList2 * operatorStrList1

def excitationOperator(CCorder = 2):
    pass

def hausdoffExpansion(H,T):
        expansion = deepcopy(H) 
        H_operatorlist = H.operatorStringList[0].operator + H.operatorStringList[1].operator
        for i in range(1,5):
            H = commutator(H,T)
            H_tmp = deepcopy(H)
            expansion +=  Fraction(1,factorial(i)) * H_tmp 
            
        expansion.operatorStringList = [item for item in expansion.operatorStringList if item.operator[0] in H_operatorlist]       
        return expansion

def hausdoffExpansionConnected(H,T):
        expansion = deepcopy(H)
        H_operatorlist = H.operatorStringList[0].operator + H.operatorStringList[1].operator
        for i in range(1,5):
            H = H*T
            H_tmp = deepcopy(H)
            expansion +=  Fraction(1,factorial(i)) * H_tmp 
        return expansion     

def tensorInitialization(tensor,indentlevel = 0):

    """ TA::TArray<T> B_11;
    if (not B_11.is_initialized()) {
        auto B_11_ptr = construct_empty2_tensor<T>(TA::get_default_world(), NO, NV);
        B_11 = *B_11_ptr;
    }"""    
    indent = "    "
    tensorname = "B_" + str(tensor.id)
    tensordimension = len(tensor.labels)
    emptydimension = []
    #superscript first
    tensorlabels = tensor.labels[tensordimension//2:] + tensor.labels[:tensordimension//2]
    for op in tensorlabels:
        if op.type == "h":
            emptydimension.append("NO")
        elif op.type == "p":
            emptydimension.append("NV")
        else:
            print("Not implemented!")
    dimension = ""
    for norbital in emptydimension:
        dimension += "," + norbital
    initializationcode = indent * indentlevel + "TA::TArray<T> " + tensorname + ";\n"
    initializationcode += indent * indentlevel + "if (not " + tensorname + ".is_initialized()) {\n"
    initializationcode +=  indent * indentlevel + indent + "auto " + tensorname + "_ptr = construct_empty" + str(tensordimension) + \
        "_tensor<T>(TA::get_default_world()" + dimension + ");\n"
    initializationcode += indent * indentlevel + indent + tensorname + " = *" + tensorname + "_ptr;\n"
    initializationcode += indent * indentlevel + "}\n"
    return initializationcode
def canonicalizeMOlabel(ijkl):
    holeindexes = ["i","j","k","l"]
    particleindexes = ["a","b","c","d"]
    newlabel = []
    nhole = 0
    nparticle = 0
    for item in ijkl:
        if item in holeindexes:
            newlabel.append(holeindexes[nhole])
            nhole += 1
        elif item in particleindexes:
            newlabel.append(particleindexes[nparticle])
            nparticle += 1
    return "".join(newlabel)

def getMoInts(amp):
    if amp.id != 1:
        print("Error!,must be a molecular integral")
    conventional_notation = {"i_{8}":"i","i_{9}":"j","a_{8}":"a","a_{9}":"b","i_{0}":"k","i_{1}":"l","a_{0}":"c","a_{1}":"d"}
    holeindexes = ["i","j","k","l"]
    particleindexes = ["a","b","c","d"]
    mo_ints_avail = ["abij","iabj","aibj","ijkl","abcd","abci","aijk"]
    # <ij||kl> = <ji||lk> = - <ij||lk> = - <ji||kl>
    # = <kl||ij>* = <lk||ji>* = -<lk||ij>* = -<kl||ji>*
    MOInts = ""
    mo_ints_type = []
    molabels = []
    nhole = 0
    nparticle = 0
    preMO = ""
    conj = False
    negative = False
    for item in amp.subscript + amp.superscript:
        molabels.append(conventional_notation[item.showwithoutDagger()])
        if item.type == "h":
            mo_ints_type.append(holeindexes[nhole])
            nhole += 1
        elif item.type == "p":
            mo_ints_type.append(particleindexes[nparticle])
            nparticle += 1
    # <ij||kl>
    if canonicalizeMOlabel(''.join(mo_ints_type)) in mo_ints_avail:
        mo_ints = canonicalizeMOlabel(''.join(mo_ints_type))
        preMO += "MO_dbar_" + mo_ints + "_1_ta_"
    #<ji||lk>
    elif canonicalizeMOlabel(''.join(mo_ints_type[:2][::-1] + mo_ints_type[2:][::-1])) in mo_ints_avail :
        mo_ints_type = mo_ints_type[:2][::-1] + mo_ints_type[2:][::-1]
        mo_ints = canonicalizeMOlabel(''.join(mo_ints_type))
        preMO += "MO_dbar_" + mo_ints + "_1_ta_"
        molabels = molabels[:2][::-1] + molabels[2:][::-1]
    #- <ij||lk>
    elif canonicalizeMOlabel(''.join(mo_ints_type[:2] + mo_ints_type[2:][::-1])) in mo_ints_avail :
        mo_ints_type = mo_ints_type[:2] + mo_ints_type[2:][::-1]
        mo_ints = canonicalizeMOlabel(''.join(mo_ints_type))
        preMO += "MO_dbar_" + mo_ints + "_1_ta_"
        negative = True
        molabels = molabels[:2] + molabels[2:][::-1]        
    #- <ji||kl>
    elif canonicalizeMOlabel(''.join(mo_ints_type[:2][::-1] + mo_ints_type[2:])) in mo_ints_avail :
        mo_ints_type = mo_ints_type[:2][::-1] + mo_ints_type[2:]
        mo_ints = canonicalizeMOlabel(''.join(mo_ints_type))
        preMO += "MO_dbar_" + mo_ints + "_1_ta_"
        negative = True
        molabels = molabels[:2][::-1] + molabels[2:]
    #<kl||ij>*
    elif canonicalizeMOlabel(''.join(mo_ints_type[2:] + mo_ints_type[:2])) in mo_ints_avail :
        mo_ints_type = mo_ints_type[2:] + mo_ints_type[:2]
        mo_ints = canonicalizeMOlabel(''.join(mo_ints_type))
        preMO += "MO_dbar_" + mo_ints + "_1_ta_"
        conj = True
        molabels = molabels[2:] + molabels[:2]
    #<lk||ji>*
    elif canonicalizeMOlabel(''.join(mo_ints_type[2:][::-1] + mo_ints_type[:2][::-1])) in mo_ints_avail :
        mo_ints_type = mo_ints_type[2:][::-1] + mo_ints_type[:2][::-1]
        mo_ints = canonicalizeMOlabel(''.join(mo_ints_type))
        preMO += "MO_dbar_" + mo_ints + "_1_ta_"
        conj = True
        molabels = molabels[2:][::-1] + molabels[:2][::-1]
    #-<lk||ij>*
    elif canonicalizeMOlabel(''.join(mo_ints_type[2:][::-1] + mo_ints_type[:2])) in mo_ints_avail :
        mo_ints_type = mo_ints_type[2:][::-1] + mo_ints_type[:2]
        mo_ints = canonicalizeMOlabel(''.join(mo_ints_type))
        preMO += "MO_dbar_" + mo_ints + "_1_ta_"
        conj = True
        negative = True    
        molabels = molabels[2:][::-1] + molabels[:2]
    #-<kl||ji>*
    elif canonicalizeMOlabel(''.join(mo_ints_type[2:] + mo_ints_type[:2][::-1])) in mo_ints_avail :
        mo_ints_type = mo_ints_type[2:] + mo_ints_type[:2][::-1]
        mo_ints = canonicalizeMOlabel(''.join(mo_ints_type))
        preMO += "MO_dbar_" + mo_ints + "_1_ta_"
        conj = True
        negative = True 
        molabels = molabels[2:] + molabels[:2][::-1]
    if not preMO:
        print("MO_ints not available")
        print(mo_ints)
        print(amp)
    if negative:
            MOInts += "-"
    mo_labels = ",".join(molabels)
    if not conj:
        MOInts += " this->" + preMO + "(\"" + mo_labels + "\")"
    elif conj :
        MOInts += " conj(this->" + preMO + "(\"" + mo_labels + "\"))"
    return MOInts    

def getAmplitude(amp, isOld = False):
    amplen = len(amp.subscript)
    conventional_notation = {"i_{8}":"i","i_{9}":"j","a_{8}":"a","a_{9}":"b","i_{0}":"k","i_{1}":"l","a_{0}":"c","a_{1}":"d"}
    amplitude_type = []
    for item in amp.superscript + amp.subscript:
        amplitude_type.append(conventional_notation[item.showwithoutDagger()])
    amplitude_labels = ",".join(amplitude_type)
    if not isOld:
        t_ta = "this->t" + str(amplen) + "_1_ta_" +"(\"" + amplitude_labels + "\")"
    else:
        t_ta = "T" + str(amplen) + "_old" +"(\"" + amplitude_labels + "\")"
    return t_ta

def getTensor(tensor):
    tensordimension = len(tensor.labels)
    tensorlabels_indexed = tensor.labels[tensordimension//2:] + tensor.labels[:tensordimension//2]
    conventional_notation = {"i_{8}":"i","i_{9}":"j","a_{8}":"a","a_{9}":"b","i_{0}":"k","i_{1}":"l","a_{0}":"c","a_{1}":"d"}
    tensorlabels_conventional = []
    for item in tensorlabels_indexed:
        tensorlabels_conventional.append(conventional_notation[item.showwithoutDagger()])
    conventionaltensorlabels = ",".join(tensorlabels_conventional)
    tensorname = "B_" + str(tensor.id) + "(\"" + conventionaltensorlabels + "\")"
    return tensorname
def getFock(amp):
    focktype = ""
    conventional_notation = {"i_{8}":"i","i_{9}":"j","a_{8}":"a","a_{9}":"b","i_{0}":"k","i_{1}":"l","a_{0}":"c","a_{1}":"d"}
    if amp.superscript[0].type == "h":
        focktype += "o"
    else:
        focktype += "v"
    if amp.subscript[0].type == "h":
        focktype += "o"
    else:
        focktype += "v"
    focklabels = []
    for item in amp.superscript + amp.subscript:
        focklabels.append(conventional_notation[item.showwithoutDagger()])
    fockcode = "F_" + focktype + "_ta_(\"" + ",".join(focklabels) + "\")"
    return fockcode
def getGeneralAmp(amp,isOld = False):
    if amp.id == 0:
        return getAmplitude(amp,isOld)
    elif amp.id == 1:
        return getMoInts(amp)
    elif amp.id == 2:
        return getFock(amp)
def processPermutedIntermediates(lst):
    #lst:[[P_1,P_2,...,P_n],tensor,amplitude]
    #return a list with 2^n elements without permutation operators:
    #[[1,tensor,amplitude],[-1,tensor',amplitude']...]
    original = [1] + lst[1:]
    unpacked = []
    unpacked.append(original)
    if len(lst[0]) == 1:
        originalindexes = lst[0][0].subscript + lst[0][0].superscript 
        tmp1 = deepcopy(original)
        tmp1[0] = -1
        #swap for tensor and amplitude
        tmp1[1] = tmp1[1].swap(originalindexes,list(reversed(originalindexes)))
        tmp1[2] = tmp1[2].swap(originalindexes,list(reversed(originalindexes)))
        unpacked.append(tmp1)
    elif len(lst[0]) == 2:
        originalindexes1 = lst[0][1].subscript + lst[0][1].superscript 
        tmp1 = deepcopy(original)
        tmp1[0] = -1
        #swap for tensor and amplitude
        tmp1[1] = tmp1[1].swap(originalindexes1,list(reversed(originalindexes1)))
        tmp1[2] = tmp1[2].swap(originalindexes1,list(reversed(originalindexes1)))
        unpacked.append(tmp1)   
        tmp2 = deepcopy(tmp1)
        tmp2[0] = 1
        originalindexes0 = lst[0][0].subscript + lst[0][0].superscript        
        #swap for tensor and amplitude
        tmp2[1] = tmp2[1].swap(originalindexes0,list(reversed(originalindexes0)))
        tmp2[2] = tmp2[2].swap(originalindexes0,list(reversed(originalindexes0)))
        unpacked.append(tmp2)     
        tmp3 = deepcopy(original)
        tmp3[0] = -1
        #swap for tensor and amplitude
        tmp3[1] = tmp3[1].swap(originalindexes0,list(reversed(originalindexes0)))
        tmp3[2] = tmp3[2].swap(originalindexes0,list(reversed(originalindexes0)))        
        unpacked.append(tmp3)
    return unpacked
    

def formIntermediate(ot, parenttensor):
    #take an operationtree which is the result of first-round factorization
    #as the argument
    #TODO: Collect intermediate tensor declaration to global
    indent = "    "
    layer1 = ""
    layer2 = ""
    layer3 = ""    
    code = "template <typename T>\n"
    parenttensorname = "B_" + str(parenttensor.id)
    code += "void CC<T>::form" + parenttensorname + "() {\n"
    code += "    size_t NO = this->ref_.nO;\n    size_t NV = this->ref_.nV;\n"
    code += tensorInitialization(parenttensor,1)
    if ot.unfactorizable:
        for operatorStr in ot.unfactorizable:
            if len(operatorStr.amplitude) > 2:
                print("unfactorizable not fully binary")
            else:
                if len(operatorStr.amplitude) == 1:
                    code += indent + getTensor(parenttensor) + " += " + str(operatorStr.coefficient) + " * "\
                         + getGeneralAmp(operatorStr.amplitude[0][0]) + ";\n"
                else:
                    code += indent +  getTensor(parenttensor) + " += " + str(operatorStr.coefficient) + " * "\
                         +getGeneralAmp(operatorStr.amplitude[0][0]) + " * "\
                           + getGeneralAmp(operatorStr.amplitude[1][0]) + ";\n"                    
    if ot.factorizable:
        for i in range(len(ot.factorizable)):
            code += tensorInitialization(ot.factorizable[i][-2],1)
            if ot.children[i].children:
                for j in range(len(ot.children[i].factorizable)):
                    code += tensorInitialization(ot.children[i].factorizable[j][-2],1)
                if ot.children[i].children[j].children:
                    print("Not supported!")
        for i in range(len(ot.factorizable)):
            if len(ot.factorizable[i]) == 2:
                layer1 += indent + getTensor(parenttensor) + " += " + \
                    getTensor(ot.factorizable[i][-2]) + " * "+ getGeneralAmp(ot.factorizable[i][-1]) + ";\n"
            elif len(ot.factorizable[i]) == 3:
                unpackedlist = processPermutedIntermediates(ot.factorizable[i])
                for unpacked in unpackedlist:
                    layer1 += indent + getTensor(parenttensor) + " += " + str(unpacked[0]) + " * "\
                          + getTensor(unpacked[1]) + " * "+ getGeneralAmp(unpacked[2]) + ";\n"
            else:
                print("Not implemented!")
            if ot.children[i].unfactorizable:
                for operatorStr in ot.children[i].unfactorizable:
                    if len(operatorStr.amplitude) > 2:
                        print("unfactorizable not fully binary")
                    else:
                        if len(operatorStr.amplitude) == 1:
                            layer2 += indent + getTensor(ot.factorizable[i][-2]) + " += " + str(operatorStr.coefficient) + " * "\
                                 + getGeneralAmp(operatorStr.amplitude[0][0]) + ";\n"
                        else:
                            layer2 += indent +  getTensor(ot.factorizable[i][-2]) + " += " + str(operatorStr.coefficient) + " * "\
                                 +getGeneralAmp(operatorStr.amplitude[0][0]) + " * "\
                                   + getGeneralAmp(operatorStr.amplitude[1][0]) + ";\n"                   
            if ot.children[i].factorizable:
                for k in range(len(ot.children[i].factorizable)):
                    if len(ot.children[i].factorizable[k]) == 2:
                        layer2 += indent + getTensor(ot.factorizable[i][-2]) + " += " + \
                            getTensor(ot.children[i].factorizable[k][-2]) + " * "+ getGeneralAmp(ot.children[i].factorizable[k][-1]) + ";\n"
                    elif len(ot.children[i].factorizable[k]) == 3:
                        unpackedlist = processPermutedIntermediates(ot.children[i].factorizable[k])
                        for unpacked in unpackedlist:
                            layer2 += indent + getTensor(ot.factorizable[i][-2]) + " += " + str(unpacked[0]) + " * "\
                                  + getTensor(unpacked[1]) + " * "+ getGeneralAmp(unpacked[2]) + ";\n"
            if ot.children[i].children:
                for l in range(len(ot.children[i].children)):
                    if ot.children[i].children[l].factorizable or ot.children[i].children[l].children:
                        print("Not implemented!")
                    else:
                        for operatorStr in ot.children[i].children[j].unfactorizable:
                            if len(operatorStr.amplitude) > 2:
                                print("unfactorizable not fully binary")
                            else:
                                if len(operatorStr.amplitude) == 1:
                                    layer3 += indent + getTensor(ot.children[i].factorizable[l][-2]) + " += " + str(operatorStr.coefficient) + " * "\
                                         + getGeneralAmp(operatorStr.amplitude[0][0]) + ";\n"
                                else:
                                    layer3 += indent +  getTensor(ot.children[i].factorizable[l][-2]) + " += " + str(operatorStr.coefficient) + " * "\
                                         +getGeneralAmp(operatorStr.amplitude[0][0]) + " * "\
                                           + getGeneralAmp(operatorStr.amplitude[1][0]) + ";\n"        
    code += layer3 + layer2 + layer1
    code += "}\n"
    return  code
        
def formUpdate(ot,order):\
    #take an operation tree as the argument, only calculate ot.factorizable
    #and ot.unfactorizable
    indent = "    "
    if order == 2:
        code = "template <typename T>\n"
        code += "void CC<T>::updateT2_ta(TArrayT T1_old, TArrayT T2_old) {\n"
        for operatorStr in ot.unfactorizable:
            if len(operatorStr.amplitude) > 2:
                print("unfactorizable not fully binary")
            else:
                if len(operatorStr.amplitude) == 1:
                    code += indent + "this->t2_1_ta_(\"a,b,i,j\") += " + str(operatorStr.coefficient) + " * "\
                         + getGeneralAmp(operatorStr.amplitude[0][0],True) + ";\n"
                else:
                    code += indent + "this->t2_1_ta_(\"a,b,i,j\") += " +  str(operatorStr.coefficient) + " * "\
                         +getGeneralAmp(operatorStr.amplitude[0][0],True) + " * "\
                           + getGeneralAmp(operatorStr.amplitude[1][0],True) + ";\n"    
        for i in range(len(ot.factorizable)):
            if len(ot.factorizable[i]) == 2:
                code += indent + "this->t2_1_ta_(\"a,b,i,j\") += " + \
                    getTensor(ot.factorizable[i][-2]) + " * "+ getGeneralAmp(ot.factorizable[i][-1],True) + ";\n"
            elif len(ot.factorizable[i]) == 3:
                unpackedlist = processPermutedIntermediates(ot.factorizable[i])
                for unpacked in unpackedlist:
                    code += indent + "this->t2_1_ta_(\"a,b,i,j\") += " +  str(unpacked[0]) + " * "\
                          + getTensor(unpacked[1]) + " * "+ getGeneralAmp(unpacked[2],True) + ";\n"
            else:
                print("Not implemented!") 
        code += indent + "this->t2_1_ta_(\"a,b,i,j\") += T2_old(\"a,b,i,j\") / eps_ta(\"a,b,i,j\");\n"
        code += indent + "this->t2_1_ta_(\"a,b,i,j\") += this->t2_1_ta_(\"a,b,i,j\") * eps_ta(\"a,b,i,j\");\n"
        code += "}\n"
        return code
    elif order == 1:
        code = "template <typename T>\n"
        code += "void CC<T>::updateT1_ta(TArrayT T1_old, TArrayT T2_old) {\n"
        for operatorStr in ot.unfactorizable:
            if len(operatorStr.amplitude) > 2:
                print("unfactorizable not fully binary")
            else:
                if len(operatorStr.amplitude) == 1:
                    code += indent + "this->t1_1_ta_(\"a,i\") += " + str(operatorStr.coefficient) + " * "\
                         + getGeneralAmp(operatorStr.amplitude[0][0],True) + ";\n"
                else:
                    code += indent + "this->t1_1_ta_(\"a,i\") += " +  str(operatorStr.coefficient) + " * "\
                         +getGeneralAmp(operatorStr.amplitude[0][0],True) + " * "\
                           + getGeneralAmp(operatorStr.amplitude[1][0],True) + ";\n"    
        for i in range(len(ot.factorizable)):
            if len(ot.factorizable[i]) == 2:
                code += indent + "this->t1_1_ta_(\"a,i\") += " + \
                    getTensor(ot.factorizable[i][-2]) + " * "+ getGeneralAmp(ot.factorizable[i][-1],True) + ";\n"
            elif len(ot.factorizable[i]) == 3:
                unpackedlist = processPermutedIntermediates(ot.factorizable[i])
                for unpacked in unpackedlist:
                    code += indent + "this->t1_1_ta_(\"a,i\") += " +  str(unpacked[0]) + " * "\
                          + getTensor(unpacked[1]) + " * "+ getGeneralAmp(unpacked[2],True) + ";\n"
            else:
                print("Not implemented!") 
        code += "}\n"
        return code        

def getCorrE(ot):
    pass