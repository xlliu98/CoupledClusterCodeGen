from Functions import *
from fractions import Fraction
import itertools
from copy import deepcopy

class operator():
    def __init__(self, type="unknown", dagger=False,index=0):
        self.type, self.dagger, self.index = type, dagger, index

    def __repr__(self):
        if  [self.type, self.dagger] == ["p",True]:
            return "a_{" + str(self.index) + "}^{\dag}"
        elif [self.type, self.dagger] == ["p",False]:
            return "a_{" + str(self.index) + "}"
        elif [self.type, self.dagger] == ["h",False]:
            return "i_" + str(self.index) +"}"
        elif [self.type, self.dagger] == ["h",True]:
            return "i_{" + str(self.index) + "}^{\dag}"
        elif [self.type, self.dagger] == ["g",False]:
            return "p_{" + str(self.index) +"}"
        elif [self.type, self.dagger] == ["g",True]:
            return "p_{" + str(self.index) + "}^{\dag}"    
    def showwithoutDagger(self):
        if  self.type == "p":
            return "a_{" + str(self.index) +"}"
        elif self.type == "h":
            return "i_{" + str(self.index) +"}"
        elif self.type  == "g":
            return "p_{" + str(self.index) +"}"
    def __mul__(self, another):
        return operatorStr(operator = [self, another])

    def __rmul__(self, coefficient):
        return operatorStr(coefficient = coefficient, operator = [self])
    
    def __add__(self, another):
        return operatorStrList([operatorStr(operator = [self]), operatorStr(operator = [another])])
    def __len__(self):
        return 1
    def __neg__(self):
        return operatorStr(coefficient = -1, operator = [self])
    def __sub__(self, another):
        if self.isEqualto(another):
            return 0
        else: return operatorStrList([operatorStr(operator = [self]),operatorStr(coefficient = -1, operator = [another])])
    def __eq__(self, another):
        if (self.type == another.type) and (self.dagger == another.dagger) and (self.index == another.index): return True
        else: return False
    def __lt__(self, another):#First compare type, hole < particle < general, then daggered > not daggered.
        if self.type != another.type:
            if self.type == 'g':
                return False
            elif self.type == 'h':
                return True
            elif self.type == 'p' and another.type == 'h':
                return False
            else: return True
        elif self.dagger != another.dagger:
            return not self.dagger and another.dagger
        else: 
            return self.index < another.index

    def isEqualto(self, another):
        if (self.type == another.type) and (self.dagger == another.dagger) and (self.index == another.index): 
            return True
        else: 
            return False
    def isGreaterThan(self,  another):
        pass
    def isIn(self,operatorStr):
        for op in operatorStr.operatorString:
            if self.isEqualto(op):
                return True
        return False
    def isSimilarto(self,another):
        if self.type == another.type and self.dagger == another.dagger:
            return True
        else: 
            return False
    def canContract(self,another):
        if self.type == "g" and another.type != self.type and another.dagger != self.dagger: # no internal contractions.
            return True
        elif [self.type, self.dagger] == ["h",True]:
            if not another.dagger and another.type != "p":
                return True
            else :
                return False
        elif [self.type, self.dagger] == ["p",False]:
            if another.dagger and another.type != "h":
                return True
            else:
                return False
        else: 
            return False

class operatorStr():
    def __init__(self, coefficient = Fraction(1,1), permutation = [], summation = [], amplitude = [], operator=[]):
        # summation, permutation, amplitude and operators can be a list of the corresponding object.
        self.coefficient = coefficient
        self.summation = summation
        self.permutation = permutation
        self.amplitude = amplitude
        self.operator = operator

    
    def __repr__(self):
        if self.coefficient == 1:
            latexString = "+"
        elif self.coefficient == -1:
            latexString = "-"
        elif self.coefficient > 0:
            latexString = "+" + str(self.coefficient)
        else : 
            latexString = str(self.coefficient)
        for permutation in list(itertools.chain(*self.permutation)):
            latexString += str(permutation)
        for summation in list(itertools.chain(*self.summation)):
            latexString += str(summation)
        for amplitude in list(itertools.chain(*self.amplitude)):
            latexString += str(amplitude)
        for operator in list(itertools.chain(*self.operator)):
            latexString += str(operator)
        return latexString
    
    def canonicalize(self):
#        self.permutation.sort()
        self.deleteEmpty()
        self.summation.sort()
        for item in self.amplitude: 
            if item[0].id == 1 or (item[0].id == 0 and len(item[0].subscript) == 2):#Only for Double excitations now
                if item[0].subscript[0].index > item[0].subscript[1].index:
                    item[0].subscript[0], item[0].subscript[1] = item[0].subscript[1], item[0].subscript[0]
                    self.coefficient *= (-1)
                if item[0].superscript[0].index > item[0].superscript[1].index:
                    item[0].superscript[0], item[0].superscript[1] = item[0].superscript[1], item[0].superscript[0]
                    self.coefficient *= (-1)
        self.amplitude.sort(reverse=True)
        if self.operator:
            whereIsH = 0
            sort = True
            for i in range(len(self.operator)):
                if self.operator[i][0].type == "g":
                    whereIsH = i
                    break
            for i in range(whereIsH+1,len(self.operator)):
                if len(self.operator[i])%2 == 1:
                    sort = False
                    break
            if sort:
                self.operator[whereIsH + 1:] = deepcopy(sorted(self.operator[whereIsH + 1:]))
            
    def makeDistinctLabel(self):
        #dict ={"h":0,"g":0,"p":0}
        teststr = self.duplicate()
        summationindexes = deepcopy(list(itertools.chain(*[item[0].indexes for item in teststr.summation])))
        if teststr.summation:
            dict = {}
            for summation in teststr.summation:
                for op in summation[0].indexes:
                    if op.type != "g":
                        if op.type not in dict.keys():
                            op.index = 0
                            dict[op.type] = 1
                        else:
                            op.index = dict[op.type]
                            dict[op.type] += 1
        if teststr.operator:
            dict = {}
            for opstr in teststr.operator:
                for i in range(len(opstr)):
                    if opstr[i].type != "g" and opstr[i] in summationindexes:
                        if len(opstr) > 1 and i+1 < len(opstr) and opstr[i].type == opstr[i+1].type and opstr[i] > opstr[i+1]:
                            if opstr[i+1].type not in dict.keys():
                                opstr[i+1].index = 0
                                opstr[i].index = 1
                                dict[opstr[i+1].type] = 2
                            else:
                                opstr[i+1].index = dict[opstr[i+1].type]
                                dict[opstr[i+1].type] += 1
                                opstr[i].index = dict[opstr[i].type]
                                dict[opstr[i].type] += 1
                            break
                        else:
                            if opstr[i].type not in dict.keys():
                                opstr[i].index = 0
                                dict[opstr[i].type] = 1
                            else:
                                opstr[i].index = dict[opstr[i].type]
                                dict[opstr[i].type] += 1
                            
        if teststr.amplitude:
            dict = {}
            for amplitudestr in teststr.amplitude:
                for op in amplitudestr[0].subscript + amplitudestr[0].superscript:
                    if op.type != "g" and op in summationindexes:
                        if op.type not in dict.keys():
                            op.index = 0
                            dict[op.type] = 1
                        else:
                            op.index = dict[op.type]
                            dict[op.type] += 1
        return teststr
    
    def relabel(self):
        if self.summation:
            summationindexes = deepcopy(list(itertools.chain(*[item[0].indexes for item in self.summation])))
            summationindexes.sort()
            oldsum = deepcopy(summationindexes)
            dict = {}
            for op in summationindexes:
                    if op.type != "g":
                        if op.type not in dict.keys():
                            op.index = 0
                            dict[op.type] = 1
                        else:
                            op.index = dict[op.type]
                            dict[op.type] += 1
            self = self.swap(oldsum,summationindexes)
            #for item in self.amplitude:
            #    for op in oldsum:
            #        if item[0].hasOperator(op):
            #            newop = summationindexes[oldsum.index(op)]
            #            item[0].replace(op,newop)
            self.summation = [[summation(summationindexes)]]
            return self
        else:
            return self
#                    opold = deepcopy(op)
#                    op.index = dict[op.type]
#                    dict[op.type] += 1
#                    for sumstr in self.summation:
#                        if sumstr[0].hasOperator(opold):
#                            sumstr[0].replace(opold,op) 
#                    for amplitudestr in self.amplitude:
#                        if amplitudestr[0].hasOperator(opold):
#                            amplitudestr[0].replace(opold,op)
#

#         
#        similaroplist = []
#        NotSimilar = True
#        oplist = []
#        for item in self.operator[1:]:
#            tmplist = [[]]
#            for op in item:
#                tmplist[0].append(deepcopy(op))
#            oplist = oplist + tmplist
#        for item in oplist:
#            for op in item:
#                NotSimilar = True
#                if similaroplist:
#                    for op_to_compare in similaroplist:
#                        if op.isSimilarto(op_to_compare):
#                            op.index = op_to_compare.index + 1
#                            op_to_compare.index = op.index
#                            NotSimilar = False
#                    if NotSimilar:
#                        similaroplist.append(deepcopy(op))
#                else: 
#                    similaroplist.append(deepcopy(op))
#        
#        self.operator[1:] = deepcopy(oplist)
#        self.summation = [[summation(item)] for item in self.operator]
#        Hamiltonian = self.operator[0]
#        self.amplitude = [[amplitude(Hamiltonian[:len(Hamiltonian)//2],list(reversed(Hamiltonian[len(Hamiltonian)//2:])), id = 1 if len(Hamiltonian) == 4 else 2)]]
#        self.amplitude = self.amplitude + [[amplitude(item[len(item)//2:],list(reversed(item[:len(item)//2])))] for item in self.operator[1:]]
#    
#

#        for op in list(itertools.chain(*self.operator))[1:] :
#            for i in range(len(similaroplist)):
#                if op.isEqualto(similaroplist[i]):
#                    op.index = similaroplist[i].index + 1
#                    similaroplist[i].index = op.index
#                else: 
#                    NotSimilar = True
#            if NotSimilar:
#                similaroplist.append(op)
#            print(op.index)
        
    def contract(self):#Contract recursively, return an operatorStrList.
        self.deleteEmpty()
        if self.isFullyContracted():
            return operatorStrList([self])
        else:
            newOperatorStringList = operatorStrList()
            first = self.operator[0][0]
            optoContract = [item for item in list(itertools.chain(*self.operator))[1:] if first.canContract(item)]
            if not optoContract:
                return operatorStrList()
            else:
                for item in optoContract:
                    newOperatorStr = self.duplicate()
                    newOperatorStr.doSingleContraction(first,item)
                    newOperatorStringList += newOperatorStr
                newOperatorStringList.deleteVanishingTerm()
            #    newOperatorStringList.relabel()
                newOperatorStringList.canonicalize()
                newOperatorStringList.combine()
                return newOperatorStringList.contract()
                    

    def doSingleContraction(self,first,another):
        parity = list(itertools.chain(*self.operator)).index(another) + 1
        self.coefficient *= (-1)**parity

        firstInSum = first in list(itertools.chain(*[item[0].indexes for item in self.summation]))
        if firstInSum:
            for item in self.summation:
                if first in item[0].indexes:
                    del item[0].indexes[item[0].indexes.index(first)] 
                    break
            for item in self.amplitude:
                if item[0].hasOperator(first):
                    item[0].replace(first,another)
                    break
        
        elif not firstInSum :
            for item in self.summation:
                if another in item[0].indexes:
                    del item[0].indexes[item[0].indexes.index(another)]
                    break
            for item in self.amplitude:
                if item[0].hasOperator(another):
                    item[0].replace(another,first)
                    break
        
        del self.operator[0][0]
        for item in self.operator:
            if another in item:
                del item[item.index(another)]
                break
        self.deleteEmpty()

    def __mul__(self, another):
        if isinstance(another, operatorStr):
            return operatorStr(coefficient = self.coefficient * another.coefficient, permutation = self.permutation + another.permutation, summation = self.summation + another.summation, amplitude = self.amplitude + another.amplitude,operator = self.operator + another.operator)
        elif isinstance(another, operator):
            return operatorStr(coefficient = self.coefficient, permutation = self.permutation, summation = self.summation, amplitude = self.amplitude, operator = self.operator.append(another))
    
    def __add__(self,another):#add two operatorStr, return operatorStrList
        if isinstance(another, operatorStr):
            return operatorStrList([self,another])
    def __rmul__(self, coefficient):#multiply one operator with a number
        return operatorStr(self.coefficient * coefficient, self.permutation, self.summation, self.amplitude, self.operator)

    def __neg__(self):
        return operatorStr(-1 * self.coefficient,  self.permutation, self.summation, self.amplitude, self.operator)
    def __sub__(self,another):
        if self.isEqualto(another):
            return 0
        else : return operatorStrList([self, -another])
    def __eq__(self, another):
        if (self.coefficient == another.coefficient) and (self.permutation == another.permutation) and (self.summation == another.summation) and (self.amplitude == another.amplitude) and (self.operator == another.operator): 
            return True
        else: 
            return False
    def isSimilarto(self,another):
        if (self.permutation == another.permutation) and (self.summation == another.summation) and (self.amplitude == another.amplitude) and (self.operator == another.operator): 
            return True
        else: 
            return False
    def isCyclicto(self,another):#return False if self is not cyclic similar to another, return the similar term if else.
        if self.hastheSameFormas(another):
            holelist = [item for item in self.summation[0][0].indexes if item.type == "h"]
            particlelist = [item for item in self.summation[0][0].indexes if item.type == "p"]
            hlists = []
            plists = []
            if len(holelist) > 1:
                hlists = [list(item) for item in list(itertools.permutations(holelist))][1:]
            if len(particlelist) > 1:
                plists = [list(item) for item in list(itertools.permutations(particlelist))][1:]
            if not hlists and not plists:
                return False
            elif hlists and not plists:
                for hlist in hlists:
                    tmp = another.swap(holelist,hlist)
                    tmp.canonicalize()
                    if self.isSimilarto(tmp):
                        return tmp
                return False
            elif plists and not hlists:
                for plist in plists:
                    tmp = another.swap(particlelist,plist)
                    tmp.canonicalize()
                    if self.isSimilarto(tmp):
                        return tmp
                return False
            elif plists and hlists:
                plists.append(particlelist)
                hlists.append(holelist)
                for plist in plists:
                    for hlist in hlists:
                        tmp = another.swap(holelist,hlist)
                        tmp1 = tmp.swap(particlelist,plist)
                        tmp1.canonicalize()
                        if self.isSimilarto(tmp1):
                            return tmp1
                return False
        else:
            return False
    def swap(self, originallist, targetlist):
        tmp = self.duplicate()
        for item in tmp.amplitude:
            for i in range(len(item[0].subscript)):
                if item[0].subscript[i] in originallist:
                    item[0].subscript[i] = targetlist[originallist.index(item[0].subscript[i])]
                if item[0].superscript[i] in originallist:
                    item[0].superscript[i] = targetlist[originallist.index(item[0].superscript[i])]
        return tmp
    def isPermutableto(self,another):#Can only give binary permutations for now, if true, return the permutation list. TODO use npair//2 to get more pairs
        isPermutableto = False
        if self.hastheSameFormas(another) and self.coefficient == -another.coefficient:
            summationindexes = self.summation[0][0].indexes
            npair = -1
            permutationlist = []
            for i in range(len(self.amplitude)):
                for j in range(len(self.amplitude[i][0].subscript)):
                    selfampij = self.amplitude[i][0].subscript[j]
                    anotherampij = another.amplitude[i][0].subscript[j]
                    if selfampij != anotherampij:
                        if selfampij not in summationindexes and anotherampij not in summationindexes:
                            npair += 1
                            if npair == 0:
                                permutationlist.append(selfampij)
                                permutationlist.append(anotherampij)
                            elif npair == 1:
                                if  [selfampij , anotherampij] == [permutationlist[1] , permutationlist[0]]:
                                    isPermutableto = permutationlist
                            elif npair > 1:
                                isPermutableto = False
                    selfampij = self.amplitude[i][0].superscript[j]
                    anotherampij = another.amplitude[i][0].superscript[j]
                    if selfampij != anotherampij:
                        if selfampij not in summationindexes and anotherampij not in summationindexes:
                            npair += 1
                            if npair == 0:
                                permutationlist.append(selfampij)
                                permutationlist.append(anotherampij)
                            elif npair == 1:
                                if  [selfampij , anotherampij] == [permutationlist[1] , permutationlist[0]]:
                                    isPermutableto = permutationlist
                            elif npair > 1:
                                isPermutableto = False
            return isPermutableto
        else:
            return isPermutableto
    def isPermutabletobyFullCommonIndex(self,another):
        if self.hastheSameFormas(another):
            holelist = [item for item in self.summation[0][0].indexes if item.type == "h"]
            particlelist = [item for item in self.summation[0][0].indexes if item.type == "p"]
            hlists = []
            plists = []
            if len(holelist) > 1:
                hlists = [list(item) for item in list(itertools.permutations(holelist))][1:]
            if len(particlelist) > 1:
                plists = [list(item) for item in list(itertools.permutations(particlelist))][1:]
            if not hlists and not plists:
                return False
            if hlists and not plists:
                for hlist in hlists:
                    tmp = another.swap(holelist,hlist)
                    tmp.canonicalize()
                    if self.isPermutableto(tmp):
                        return self.isPermutableto(tmp)
                return False
            elif plists and not hlists:
                for plist in plists:
                    tmp = another.swap(particlelist,plist)
                    tmp.canonicalize()
                    if self.isPermutableto(tmp):
                        return self.isPermutableto(tmp)
                return False
            elif plists and hlists:
                plists.append(particlelist)
                hlists.append(holelist)
                for plist in plists:
                    for hlist in hlists:
                        tmp = another.swap(holelist,hlist)
                        tmp1 = tmp.swap(particlelist,plist)
                        tmp1.canonicalize()
                        if self.isPermutableto(tmp1):
                            return self.isPermutableto(tmp1)
                return False
            else:
                return False                
    def hastheSameFormas(self,another):
        if self.permutation == another.permutation and self.summation == another.summation and len(self.amplitude) == len(another.amplitude):
            istheSame = True
            for i in range(len(self.amplitude)):
                if not(self.amplitude[i][0].id == another.amplitude[i][0].id and len(self.amplitude[i][0].subscript) == len(another.amplitude[i][0].subscript)):
                    istheSame = False
                    break
            return istheSame
        else:
            return False
    def canonicalizewithoutChangingAmplitudes(self):#for post-processing of cc equations, change integrals to canonical order
        self.deleteEmpty()
        self.summation.sort()
        for item in self.amplitude: 
            if item[0].id == 1:#Only for Double excitations now
                if item[0].subscript[0].index > item[0].subscript[1].index:
                    item[0].subscript[0], item[0].subscript[1] = item[0].subscript[1], item[0].subscript[0]
                    self.coefficient *= (-1)
                if item[0].superscript[0].index > item[0].superscript[1].index:
                    item[0].superscript[0], item[0].superscript[1] = item[0].superscript[1], item[0].superscript[0]
                    self.coefficient *= (-1)
        self.amplitude.sort(reverse=True)

    def extractAllPermutation(self):#only for double excitations for now. Assume every swap creates a -1.
        if self.summation:
            summationindexes = self.summation[0][0].indexes
            internalhlist = [op for op in summationindexes if op.type == "h"]
            internalplist = [op for op in summationindexes if op.type == "p"]
            externalhlist = []
            externalplist = []
            for item in self.amplitude:
                ampindexes = item[0].subscript + item[0].superscript
                externalhlist += [op for op in ampindexes if op not in summationindexes and op.type == "h"]
                externalplist += [op for op in ampindexes if op not in summationindexes and op.type == "p"]
            if self.permutation:
                for permutations in self.permutation:
                    externalhlist = [op for op in externalhlist if op not in permutations[0].subscript + permutations[0].superscript]
                    externalplist = [op for op in externalplist if op not in permutations[0].subscript + permutations[0].superscript]
            if externalplist:
                if len(internalplist) == 2:
                    tmp1 = self.duplicate()
                    tmp1 = tmp1.swap(externalplist,externalplist[::-1])
                    tmp1.canonicalizewithoutChangingAmplitudes()
                    tmp2 = tmp1.duplicate()
                    tmp2 = tmp2.swap(internalplist,internalplist[::-1])
                    tmp2.canonicalizewithoutChangingAmplitudes()
                    tmp2.coefficient *= -1
                    if tmp2 == self:
                        if self.permutation:
                            if self.permutation[-1] !=\
                         [permutation(subscript = [externalplist[0]], superscript = [externalplist[1]])]:
                                self.coefficient *= Fraction(1,2)
                                self.permutation.append([permutation(subscript = [externalplist[0]], superscript = [externalplist[1]])])
                        else :
                            self.coefficient *= Fraction(1,2)
                            self.permutation.append([permutation(subscript = [externalplist[0]], superscript = [externalplist[1]])])

                if len(internalhlist) == 2:
                    tmp1 = self.duplicate()
                    tmp1 = tmp1.swap(externalplist,externalplist[::-1])
                    tmp1.canonicalizewithoutChangingAmplitudes()
                    tmp2 = tmp1.duplicate()
                    tmp2 = tmp2.swap(internalhlist,internalhlist[::-1])
                    tmp2.canonicalizewithoutChangingAmplitudes()
                    tmp2.coefficient *= -1
                    if tmp2 == self: 
                        if self.permutation:
                            if self.permutation[-1] !=\
                         [permutation(subscript = [externalplist[0]], superscript = [externalplist[1]])]:
                                self.coefficient *= Fraction(1,2)
                                self.permutation.append([permutation(subscript = [externalplist[0]], superscript = [externalplist[1]])])
                        else :
                            self.coefficient *= Fraction(1,2)
                            self.permutation.append([permutation(subscript = [externalplist[0]], superscript = [externalplist[1]])])
                if len(internalplist) == 2 and len(internalhlist) == 2:
                    tmp1 = self.duplicate()
                    tmp1 = tmp1.swap(externalplist,externalplist[::-1])
                    tmp1.canonicalizewithoutChangingAmplitudes()
                    tmp2 = tmp1.duplicate()
                    tmp2 = tmp2.swap(internalhlist,internalhlist[::-1])
                    tmp2 = tmp2.swap(internalplist,internalplist[::-1])
                    tmp2.canonicalizewithoutChangingAmplitudes()
                    if tmp2 == self:
                        if self.permutation:
                            if self.permutation[-1] !=\
                         [permutation(subscript = [externalplist[0]], superscript = [externalplist[1]])]:
                                self.coefficient *= Fraction(1,2)
                                self.permutation.append([permutation(subscript = [externalplist[0]], superscript = [externalplist[1]])])
                        else :
                            self.coefficient *= Fraction(1,2)
                            self.permutation.append([permutation(subscript = [externalplist[0]], superscript = [externalplist[1]])])
                if len(internalplist) == 2 and len(internalhlist) == 2 and self.permutation:
                    tmp1 = self.duplicate()
                    tmp1 = tmp1.swap(externalplist,externalplist[::-1])
                    tmp1.canonicalizewithoutChangingAmplitudes()
                    tmp2 = tmp1.duplicate()
                    tmp2 = tmp2.swap(internalhlist,internalhlist[::-1])
                    tmp2 = tmp2.swap(internalplist,internalplist[::-1])
                    selfpermutation = self.permutation[0][0].subscript + self.permutation[0][0].superscript
                    tmp2 = tmp2.swap(selfpermutation,selfpermutation[::-1])
                    tmp2.canonicalizewithoutChangingAmplitudes()
                    if tmp2 == self :
                        if self.permutation:
                            if self.permutation[-1] !=\
                         [permutation(subscript = [externalplist[0]], superscript = [externalplist[1]])]:
                                self.coefficient *= Fraction(1,2)
                                self.permutation.append([permutation(subscript = [externalplist[0]], superscript = [externalplist[1]])])
                        else :
                            self.coefficient *= Fraction(1,2)
                            self.permutation.append([permutation(subscript = [externalplist[0]], superscript = [externalplist[1]])])
            if externalhlist:
                if len(internalhlist) == 2:
                    tmp1 = self.duplicate()
                    tmp1 = tmp1.swap(externalhlist,externalhlist[::-1])
                    tmp1.canonicalizewithoutChangingAmplitudes()
                    tmp2 = tmp1.duplicate()
                    tmp2 = tmp2.swap(internalhlist,internalhlist[::-1])
                    tmp2.canonicalizewithoutChangingAmplitudes()
                    tmp2.coefficient *= -1
                    if tmp2 == self :
                        if self.permutation:
                            if self.permutation[-1] !=\
                         [permutation(subscript = [externalhlist[0]], superscript = [externalhlist[1]])]:
                                self.coefficient *= Fraction(1,2)
                                self.permutation.append([permutation(subscript = [externalhlist[0]], superscript = [externalhlist[1]])])
                        else :
                            self.coefficient *= Fraction(1,2)
                            self.permutation.append([permutation(subscript = [externalhlist[0]], superscript = [externalhlist[1]])])
                if len(internalplist) == 2:
                    tmp1 = self.duplicate()
                    tmp1 = tmp1.swap(externalhlist,externalhlist[::-1])
                    tmp1.canonicalizewithoutChangingAmplitudes()
                    tmp2 = tmp1.duplicate()
                    tmp2 = tmp2.swap(internalplist,internalplist[::-1])
                    tmp2.canonicalizewithoutChangingAmplitudes()
                    tmp2.coefficient *= -1
                    if tmp2 == self :
                        if self.permutation:
                            if self.permutation[-1] !=\
                         [permutation(subscript = [externalhlist[0]], superscript = [externalhlist[1]])]:
                                self.coefficient *= Fraction(1,2)
                                self.permutation.append([permutation(subscript = [externalhlist[0]], superscript = [externalhlist[1]])])
                        else :
                            self.coefficient *= Fraction(1,2)
                            self.permutation.append([permutation(subscript = [externalhlist[0]], superscript = [externalhlist[1]])])
                if len(internalplist) == 2 and len(internalhlist) == 2:
                    tmp1 = self.duplicate()
                    tmp1 = tmp1.swap(externalhlist,externalhlist[::-1])
                    tmp1.canonicalizewithoutChangingAmplitudes()
                    tmp2 = tmp1.duplicate()
                    tmp2 = tmp2.swap(internalhlist,internalhlist[::-1])
                    tmp2 = tmp2.swap(internalplist,internalplist[::-1])
                    tmp2.canonicalizewithoutChangingAmplitudes()
                    if tmp2 == self :
                        if self.permutation:
                            if self.permutation[-1] !=\
                         [permutation(subscript = [externalhlist[0]], superscript = [externalhlist[1]])]:
                                self.coefficient *= Fraction(1,2)
                                self.permutation.append([permutation(subscript = [externalhlist[0]], superscript = [externalhlist[1]])])
                        else :
                            self.coefficient *= Fraction(1,2)
                            self.permutation.append([permutation(subscript = [externalhlist[0]], superscript = [externalhlist[1]])])
                if len(internalplist) == 2 and len(internalhlist) == 2 and self.permutation:
                    tmp1 = self.duplicate()
                    tmp1 = tmp1.swap(externalhlist,externalhlist[::-1])
                    tmp1.canonicalizewithoutChangingAmplitudes()
                    tmp2 = tmp1.duplicate()
                    tmp2 = tmp2.swap(internalhlist,internalhlist[::-1])
                    tmp2 = tmp2.swap(internalplist,internalplist[::-1])
                    selfpermutation = self.permutation[0][0].subscript + self.permutation[0][0].superscript
                    tmp2 = tmp2.swap(selfpermutation,selfpermutation[::-1])
                    tmp2.canonicalizewithoutChangingAmplitudes()
                    if tmp2 == self :
                        if self.permutation:
                            if self.permutation[-1] !=\
                         [permutation(subscript = [externalhlist[0]], superscript = [externalhlist[1]])]:
                                self.coefficient *= Fraction(1,2)
                                self.permutation.append([permutation(subscript = [externalhlist[0]], superscript = [externalhlist[1]])])
                        else :
                            self.coefficient *= Fraction(1,2)
                            self.permutation.append([permutation(subscript = [externalhlist[0]], superscript = [externalhlist[1]])])


    def duplicate(self):
        return operatorStr(coefficient = deepcopy(self.coefficient), permutation = deepcopy(self.permutation), summation = [deepcopy(item) for item in self.summation], amplitude = [deepcopy(item) for item in self.amplitude], operator = [deepcopy(item) for item in self.operator])
    def deleteEmpty(self):
        if self.operator:
            index_to_be_deleted = []
            for i in range(len(self.operator)):
                if not self.operator[i]:
                    index_to_be_deleted.append(i)
            for i in sorted(index_to_be_deleted, reverse=True):
                del self.operator[i]
        index_to_be_deleted = []
        if self.summation:
            for i in range(len(self.summation)):
                if self.summation[i][0].isEmpty():
                    index_to_be_deleted.append(i)
            for i in sorted(index_to_be_deleted, reverse=True):
                del self.summation[i]

    def isFullyContracted(self):
        self.deleteEmpty()
        if not self.operator:
            return True
        else:
            return False
    def isDisconnectedDiagram(self):
        if len(self.amplitude) > 1:
            for item in self.amplitude:
                oplist = item[0].subscript + item[0].superscript
                isDisconnected = True
                for anotheritem in [amp for amp in self.amplitude if amp[0] != item[0]]:
                    for op in oplist:
                        if anotheritem[0].hasOperator(op):
                            isDisconnected = False
                            break
                if isDisconnected:
                    return True
            return isDisconnected
    def findBestContraction(self,NO=2,NV=20):
        possibleContractions =  [list(item) for item in list(itertools.permutations(self.amplitude))]
        possibleCosts = []
        for amplist in possibleContractions:
            tmp = operatorStr()
            tmp.amplitude = amplist
            possibleCosts.append(tmp.totalContractionCost(NO,NV)) 
        bestContractionOrder = possibleContractions[possibleCosts.index(min(possibleCosts))]
        return bestContractionOrder
    def replacebyBestContractionOrder(self,NO=2,NV=20):
        self.amplitude = deepcopy(self.findBestContraction(NO,NV))
    def totalContractionCost(self,NO=2,NV=20):#return total operation cost
        #Contract the leftmost tensor and the second to the leftmost. Absorb the information to the leftmost tensor.
        #Only subscript and superscript matter in the calculation of contraction cost
        #leftmost = Tensor(subscript = self.amplitude[0][0].subscript, superscript = self.amplitude[0][0].superscript) 
        leftmost = self.amplitude[0][0].subscript + self.amplitude[0][0].superscript
        cost = 0.
        
        for i in range(1,len(self.amplitude)):
            leftmostvirtual = [op for op in leftmost if op.type == "p"]
            leftmostoccupied = [op for op in leftmost if op.type == "h"]
            totalOperatorList = self.amplitude[i][0].superscript + self.amplitude[i][0].subscript
            
            internalvirtual = [op for op in totalOperatorList if op in leftmostvirtual]
            internaloccupied = [op for op in totalOperatorList if op in leftmostoccupied]
            
            externalvirtual = [op for op in totalOperatorList if op.type == "p" and op not in internalvirtual]
            externaloccupied = [op for op in totalOperatorList if op.type == "h" and op not in internaloccupied]
            
            occupied = len(leftmostoccupied) + len(externaloccupied)
            virtual = len(leftmostvirtual) + len(externalvirtual)
            cost += NO**occupied * NV**virtual

            leftmost = [op for op in leftmost if op not in internalvirtual and op not in internaloccupied]
            leftmost = leftmost + externalvirtual + externaloccupied

        return cost
#    def generateStrengthReductionSequence(self):
#        if len(self.amplitude) == 1:
#            return [Tensor(contents = [deepcopy([self.amplitude])])]
#        if len(self.amplitude) == 2 :#return a tensor whose contents is one tensor
#            return [Tensor(contents = [[operatorStr(amplitude=deepcopy([self.amplitude[0]]))]]),\
#                Tensor(contents = [[operatorStr(amplitude=deepcopy([self.amplitude[1]]))]])]
#        else :
#            tensorlist = [Tensor(contents = [[operatorStr(amplitude=deepcopy([self.amplitude[0]]))]]),\
#                Tensor(contents = [[operatorStr(amplitude=deepcopy([self.amplitude[1]]))]])]
#            for i in range(2,len(self.amplitude)):
#                tmptensor = Tensor(contents = [[deepcopy(lasttensor)],[Tensor(contents = [[operatorStr(amplitude=deepcopy([self.amplitude[i]]))]])]])
#                tensorlist.append(tmptensor)
#                lasttensor = deepcopy(tmptensor)
#        return tensorlist
    def generateStrengthReductionSequence(self):
        if len(self.amplitude) > 2:
            tensorlist = [Tensor(contents = [operatorStr(amplitude=deepcopy(self.amplitude[:2]))])]
            for i in range(2,len(self.amplitude)):
                tmptensor = Tensor(contents = [[deepcopy(lasttensor)],[Tensor(contents = [[operatorStr(amplitude=deepcopy([self.amplitude[i]]))]])]])
                tensorlist.append(tmptensor)
                lasttensor = deepcopy(tmptensor)
        return tensorlist            
    def toRawCQsnippet(self):
        conventional_notation = {"i_{8}":"i","i_{9}":"j","a_{8}":"a","a_{9}":"b","i_{0}":"k","i_{1}":"l","a_{0}":"c","a_{1}":"d"}
        holeindexes = ["i","j","k","l","m","n"]
        particleindexes = ["a","b","c","d","e","f"]
        mo_ints_avail = ["abij","iabj","aibj","ijkl","abcd","abci","aijk"]
        if not self.permutation and self.amplitude[0][0].id == 1:
            rawCQSnippet = ""
            mo_ints_type = []
            molabels = []
            nhole = 0
            nparticle = 0
            for item in self.amplitude[0][0].subscript + self.amplitude[0][0].superscript:
                molabels.append(conventional_notation[item.showwithoutDagger()])
                if item.type == "h":
                    mo_ints_type.append(holeindexes[nhole])
                    nhole += 1
                elif item.type == "p":
                    mo_ints_type.append(particleindexes[nparticle])
                    nparticle += 1
            mo_ints = ''.join(mo_ints_type)
            mo_ints_conj = ''.join(mo_ints_type[2:]+mo_ints_type[:2])
            if mo_ints in mo_ints_avail:
                conj = False
                TArrayT = "MO_dbar_" + mo_ints + "_1_ta_"
            elif mo_ints_conj in mo_ints_avail:
                conj = True
                TArrayT = "MO_dbar_" + mo_ints_conj + "_1_ta_"
            else :
                print("mo_ints not found")
            if not conj:
                mo_labels = ','.join(molabels)
            elif conj :
                mo_labels = ','.join(molabels[2:] + molabels[:2])
            intermediateindexes = []
            for i in range(1,len(self.amplitude)):     
                if not intermediateindexes:
                    amplitudeindexes = self.amplitude[i][0].subscript + self.amplitude[i][0].superscript
                    mointsindexes = self.amplitude[0][0].subscript + self.amplitude[0][0].superscript
                    intermediateindexes = [op for op in mointsindexes if op not in amplitudeindexes] + \
                        [op for op in amplitudeindexes if op not in mointsindexes]
                elif intermediateindexes:
                    amplitudeindexes = self.amplitude[i][0].subscript + self.amplitude[i][0].superscript
                    intermediateindexes = [op for op in intermediateindexes if op not in amplitudeindexes] + \
                        [op for op in amplitudeindexes if op not in intermediateindexes]
                intermediate = "W_ta" + str(i)
                intermediate_labels = ','.join([conventional_notation[item.showwithoutDagger()] for item in intermediateindexes])
                t_ta = ""
                if len(self.amplitude[i][0].subscript) == 1 :
                    t_ta += "t1_1_ta_"
                elif len(self.amplitude[i][0].subscript) == 2 :
                    t_ta += "t2_1_ta_"
                amplitude_type = []
                for item in self.amplitude[i][0].superscript + self.amplitude[i][0].subscript:
                        amplitude_type.append(conventional_notation[item.showwithoutDagger()])
                amplitude_labels = ','.join(amplitude_type)
                
                if i == 1:
                    if not conj:
                        rawCQSnippet += intermediate + "(\"" + intermediate_labels +  "\") =" + \
                            "this->" + t_ta + "(\"" + amplitude_labels \
                             + "\")" + " * this->" + TArrayT + "(\"" + mo_labels + "\");\n"
                    elif conj :
                        rawCQSnippet += intermediate + "(\"" + intermediate_labels +  "\") =" + \
                            "this->" + t_ta + "(\"" + amplitude_labels \
                             + "\")" + " * conj(this->" + TArrayT + "(\"" + mo_labels + "\"));\n"
                else :
                    rawCQSnippet += intermediate + "(\"" + intermediate_labels +  "\") =" + \
                            "this->" + t_ta + "(\"" + amplitude_labels \
                             + "\")" + " * " + lastintermediate + "(\"" + lastintermediate_labels + "\");\n"
                lastintermediate_labels = deepcopy(intermediate_labels) 
                lastintermediate = deepcopy(intermediate)
            return rawCQSnippet

    def factorizablewith(self,another):
        if len(self.amplitude) >1 and len(another.amplitude) > 1:
            if self.amplitude[-1] == another.amplitude[-1] :
                return self.amplitude[-1]
        return False
    def factorizablewithFirstRound(self,another):
        if len(self.amplitude) >1 and len(another.amplitude) > 1:
            if self.amplitude[-1] == another.amplitude[-1]:
                return self.amplitude[-1]
            elif self.permutation or another.permutation:
                if len(self.permutation) >= len(another.permutation):#generate self permutations to find match
                    for selfpermutations in self.permutation:
                        originalorder = selfpermutations[0].subscript + selfpermutations[0].superscript
                        permutedorder = deepcopy(originalorder)
                        permutedorder.reverse()
                        selfcopy = self.duplicate()
                        selfcopy = deepcopy(selfcopy.swap(originalorder,permutedorder))
                        if selfcopy.amplitude[-1] == another.amplitude[-1]:
                            self = selfcopy.duplicate()
                            self.coefficient *= -1
                            return another.amplitude[-1]
                elif len(self.permutation) <= len(another.permutation):
                    for anotherpermutations in another.permutation:
                        originalorder = anotherpermutations[0].subscript + anotherpermutations[0].superscript
                        permutedorder = deepcopy(originalorder)
                        permutedorder.reverse()
                        anothercopy = another.duplicate()
                        anothercopy = deepcopy(anothercopy.swap(originalorder,permutedorder))
                        if self.amplitude[-1] == anothercopy.amplitude[-1]:
                            another = anothercopy.duplicate()
                            another.coefficient *= -1
                            return self.amplitude[-1]
        return False
    def maxlength(self):
        return len(self.amplitude)
    

class operatorStrList():
    def __init__(self, operatorStringList = []):
        self.operatorStringList = operatorStringList
 
    def __repr__(self):
        operatorStrListToString = ""
        for item in self.operatorStringList:
            operatorStrListToString += item.__repr__() 
        return operatorStrListToString
    def __len__(self):
        return len(self.operatorStringList)
    def __add__(self, another): # add another operatorStrList
        if isinstance(another, operatorStrList):
            return operatorStrList(self.operatorStringList + another.operatorStringList)
        elif isinstance(another, operatorStr):
            return operatorStrList(self.operatorStringList + [another])
    def __mul__(self, another):#multiplied by an operatorStr from right
        if isinstance(another, operatorStr):
            for item in self.operatorStringList:
                item.coefficient *= another.coefficient
                item.permutation += another.permutation
                item.summation += another.summation
                item.amplitude += another.amplitude
                item.operator += another.operator
            return self
        elif isinstance(another, operatorStrList):
            newOperatorStrList = []
            for operatorStr1 in self.operatorStringList:
                for operatorStr2 in another.operatorStringList:
                    newOperatorStrList.append(operatorStr1 * operatorStr2)
            return operatorStrList(newOperatorStrList)

    def __rmul__(self, another):#multiplied by an operatorStr from left
        if isinstance(another, operatorStr):
            for item in self.operatorStringList:
                item.coefficient *= another.coefficient
                item.permutation = another.permutation + item.permutation
                item.summation = another.summation + item.summation
                item.amplitude = another.amplitude + item.amplitude
                item.operator = another.operator + item.operator
            return self    
        elif isinstance(another, Fraction):
            for item in self.operatorStringList:
                item.coefficient *= another
            return operatorStrList(self.operatorStringList)
        
    def __sub__(self,another):
        for item in another.operatorStringList:
            item.coefficient *= -1
        return operatorStrList(self.operatorStringList + another.operatorStringList)
    def canonicalize(self):
        for item in self.operatorStringList:
            item.canonicalize()
    def deleteVanishingWick(self):
        l = len(self)
        if l > 0:
            index_to_be_deleted = []
            for i in range(l):
                self.operatorStringList[i].deleteEmpty()
                if self.operatorStringList[i].operator:
                    if self.operatorStringList[i].operator[0][0].type == "g":#Energy Equations 
                        if len(list(itertools.chain(*self.operatorStringList[i].operator[1:]))) != len(self.operatorStringList[i].operator[0]):
                            index_to_be_deleted.append(i)
                    elif len(self.operatorStringList[i].operator) > 1 and self.operatorStringList[i].operator[1][0].type == "g":#Amplitude Equation
                        if len(list(itertools.chain(*self.operatorStringList[i].operator[2:]))) - len(self.operatorStringList[i].operator[0])  != len(self.operatorStringList[i].operator[1]):
                            index_to_be_deleted.append(i)
            for i in sorted(index_to_be_deleted, reverse=True):
                del self.operatorStringList[i]
    def deleteVanishingTerm(self):
        
        l = len(self)
        if l > 0:
            index_to_be_deleted = []
            for i in range(l):
                dict = {"p":[0,0],"h":[0,0],"g":[0,0]}#Store the number of operators, 0 = creation, 1 = annihilation
                self.operatorStringList[i].deleteEmpty()
                if self.operatorStringList[i].operator:
                    for op in list(itertools.chain(*self.operatorStringList[i].operator)):
                        if op.dagger:
                            dict[op.type][0] += 1
                        else:
                            dict[op.type][1] += 1
                    if dict["p"][1] + dict["g"][1] < dict["p"][0]:
                        index_to_be_deleted.append(i)
                    elif dict["p"][0] + dict["g"][0] < dict["p"][1]:
                        index_to_be_deleted.append(i)
                    elif dict["h"][1] + dict["g"][1] < dict["h"][0]:
                        index_to_be_deleted.append(i)
                    elif dict["h"][0] + dict["g"][0] < dict["h"][1]:
                        index_to_be_deleted.append(i)    
            for i in sorted(index_to_be_deleted, reverse=True):
                del self.operatorStringList[i]
    
    def combineCyclicTerms(self):
        for i in range(len(self)):
            for j in range(len(self)):
                if i != j:
                    tmp = self.operatorStringList[i].isCyclicto(self.operatorStringList[j])
                    if tmp:
                        self.operatorStringList[j] = tmp
        self.combine()
    def findPermutationandCombine(self):
        index_to_be_deleted = []
        for i in range(len(self)):
            if i not in index_to_be_deleted:
                for j in range(len(self)):
                    if j != i:
                        isPermutableto = self.operatorStringList[i].isPermutableto(self.operatorStringList[j])
                        if isPermutableto:
                            index_to_be_deleted.append(j)
                            self.operatorStringList[i].permutation.append([permutation(isPermutableto[:len(isPermutableto)//2],isPermutableto[len(isPermutableto)//2:])])
        if index_to_be_deleted:
            for i in sorted(index_to_be_deleted, reverse=True):
                del self.operatorStringList[i]
    def combinebyFullPermutationofCommonIndexes(self):
        index_to_be_deleted = []
        for i in range(len(self)):
            if i not in index_to_be_deleted:
                for j in range(len(self)):
                    if j != i:
                        isPermutableto = self.operatorStringList[i].isPermutabletobyFullCommonIndex(self.operatorStringList[j])
                        if isPermutableto:
                            index_to_be_deleted.append(j)
                            self.operatorStringList[i].permutation.append([permutation(isPermutableto[:len(isPermutableto)//2],isPermutableto[len(isPermutableto)//2:])])
        if index_to_be_deleted:
            for i in sorted(index_to_be_deleted, reverse=True):
                del self.operatorStringList[i]
    def deleteDisconnectedDiagram(self):
        l = len(self)
        if l > 0:
            index_to_be_deleted = []
            for i in range(l):
                if self.operatorStringList[i].isDisconnectedDiagram():
                    index_to_be_deleted.append(i)
            for i in sorted(index_to_be_deleted, reverse=True):
                del self.operatorStringList[i]
    def relabel(self):
        self.operatorStringList = [item.relabel().duplicate() for item in self.operatorStringList]
    def makeDistinctLabel(self):
        self.operatorStringList = [item.makeDistinctLabel().duplicate() for item in self.operatorStringList]
    def combine(self):
        l = len(self)
        index_to_be_deleted = []
        for i in range(l):
            if i not in index_to_be_deleted:
                for j in range(l): 
                    if  (i != j) and (self.operatorStringList[i].isSimilarto(self.operatorStringList[j])):
                        self.operatorStringList[i].coefficient += self.operatorStringList[j].coefficient
                        index_to_be_deleted.append(j)
        for i in sorted(index_to_be_deleted, reverse=True):
            del self.operatorStringList[i]
        index_to_be_deleted = []
        l = len(self)
        for i in range(l):
            if self.operatorStringList[i].coefficient == 0:
                index_to_be_deleted.append(i)
        for i in sorted(index_to_be_deleted, reverse=True):
            del self.operatorStringList[i]
    def contract(self):
        newOpStrList = operatorStrList()
        for item in self.operatorStringList:
            newOpStrList += item.contract()
        return newOpStrList
    def replaceAllbyBestContractionOrder(self):
        for item in self.operatorStringList:
            if len(item.amplitude) > 2:
                item.replacebyBestContractionOrder()
    def test(self):
        matched = {}
        l = len(self)
        alreadyfactorized = []
        totalfactorization = []
        for i in range(l):
#            matched[i] = []
            for j in range(i+1,l) :
                if i not in alreadyfactorized and j not in alreadyfactorized:
                    item = self.operatorStringList[i].factorizablewith(self.operatorStringList[j])
                    if item:
                        totalfactorization.append(self.doBinaryFactorize())
                        matched[item[0].__repr__()] = [i,j]
                        alreadyfactorized.append(j)
                        alreadyfactorized.append(i)
                        for k in range(j+1,l) :
                            if k not in alreadyfactorized:
                                if item in self.operatorStringList[k].amplitude:
                                    alreadyfactorized.append(k)
                                    matched[item[0].__repr__()].append(k)
        print(alreadyfactorized)
        print(len(alreadyfactorized))
        print(matched)
        print([item for item in range(31) if item not in alreadyfactorized])
#                        matched[i].append(j)
#        matched = {k:v for k,v in matched.items() if v } #delete empty entries
#        print(len(matched))
#        return matched
        
#        tailamplitude = []
#        for item in self.operatorStringList:
#            if item.amplitude[-1][0] not in tailamplitude:
#                tailamplitude.append(item.amplitude[-1][0])
#        print(len(tailamplitude))
#        return ''.join([item.__repr__() for item in tailamplitude if len(item.subscript) == 2])

    def getStrengthReductionTensors(self):
        SRTs = []
        for item in self.operatorStringList:
            SRTs.append(item.generateStrengthReductionSequence())
        return SRTs
    def factorizable(self):
        if len(self) >1:
            for i in range(len(self)):
                for j in range(i+1,len(self)):
                    if self.operatorStringList[i].factorizablewith(self.operatorStringList[j]):
                        return self.operatorStringList[i].factorizablewith(self.operatorStringList[j])
        return False
    def toCQCode(self):
        pass
    def doFirstRoundFactorization(self):
        pass
    def factorize(self):
        pass
    def factorizeAll(self,iteration=0):
        operationsequence = []
        if self.factorizable:
            if iteration == 0:
                pass
            else:
                self.factorize(iteration+1)
        else:
            return self
    def extractAllPermutation(self):
        for item in self.operatorStringList:
            item.extractAllPermutation()
class summation():
    def __init__(self,indexes=[]):
        self.indexes=indexes
    def __repr__(self):
        sum = "\sum\limits_{"
        for op in self.indexes:
            sum += op.showwithoutDagger()
        sum += "}"
        return sum
    def __eq__(self, another):
        if self.indexes == another.indexes: return True
        else: return False
    def __lt__(self, another):
        return self.indexes < another.indexes
    def isEmpty(self):
        if self.indexes == []:
            return True
        else:
            return False
    def hasOperator(self,operator):
        if operator in self.indexes:
            return True
        else:
            return False
    def replace(self,op1,op2):#replace op1 with op2
        self.indexes[self.indexes.index(op1)] = op2


class amplitude():
    def __init__(self,subscript = [], superscript = [],id = 0, conjugate = False):
        # If it's a CC amplitude, id = 0, if it's a 2-e integral, id = 1, for 1-e integral, id = 2.
        self.subscript = subscript
        self.superscript = superscript
        self.id = id
        self.conjugate = conjugate
    def __repr__(self):
        subscript = ""
        superscript = ""
        for op in self.subscript:
            subscript += op.showwithoutDagger()
        for op in self.superscript:
            superscript += op.showwithoutDagger()
        latexstring = ""
        if self.id == 0:
            latexstring = "t_{" + subscript + "}^{" + superscript + "}"  
        elif self.id == 1: # Show 2-e integral, the physics package needs to be included.
            latexstring = "\\bra{" + subscript + "}$$\ket{" + superscript + "}"
        elif self.id == 2:
            latexstring = "f_{" + subscript + superscript + "}"
        if self.conjugate:
            latexstring += "^*"
            return latexstring
        else:
            return latexstring
        
    def changeConjugate(self):
        if self.conjugate:
            self.conjugate = False
        else:
            self.conjugate = True
    def __eq__(self, another):
        if self.id == another.id and \
            self.subscript == another.subscript and \
                self.superscript == another.superscript: 
            return True
        else: 
            return False

    def __lt__(self, another):
        if self.id < another.id:
            return True
        elif self.id > another.id:
            return False
        elif self.subscript < another.subscript:
            return True
        elif self.subscript > another.subscript:
            return False
        elif self.superscript < another.superscript:
            return True
        else : return False
        #if self.id > another.id:
        #    return True
        #elif self.id < another.id:
        #    return False
        #elif len(self.subscript) > len(another.subscript):
        #    return True
        #elif len(self.subscript) < len(another.subscript):
        #    return False
        #elif self.subscript < another.subscript:
        #    return True
        #elif self.subscript > another.subscript:
        #    return False
        #elif self.superscript < another.superscript:
        #    return True
        #else : return False
    def isEmpty(self):
        if self.subscript == [] and self.superscript == []:
            return True
        else :
            return False
    def hasOperator(self,operator):
        if operator in self.subscript or operator in self.superscript:
            return True
        else:
            return False    
    def replace(self,op1,op2):#replace op1 with op2
        if op1 in self.subscript:
            self.subscript[self.subscript.index(op1)] = op2
        else:
            self.superscript[self.superscript.index(op1)] = op2
    def duplicate(self):
        return amplitude(deepcopy(self.subscript),deepcopy(self.superscript),self.id,self.conjugate)
    def swap(self, originallist, targetlist):
        tmp = self.duplicate()
        for i in range(len(tmp.subscript)):
            if tmp.subscript[i] in originallist:
                tmp.subscript[i] = targetlist[originallist.index(tmp.subscript[i])]    
            if tmp.superscript[i] in originallist:
                tmp.superscript[i] = targetlist[originallist.index(tmp.superscript[i])] 
        return tmp

class permutation():
    def __init__(self,subscript = [], superscript = []):
        self.subscript = subscript
        self.superscript = superscript

    def __repr__(self):
        subscript = ""
        superscript = ""
        for op in self.subscript:
            subscript += op.showwithoutDagger()
        for op in self.superscript:
            superscript += op.showwithoutDagger()
        return "P(" + subscript + superscript + ")"

    def __eq__(self, another):
        if self.subscript == another.subscript and self.superscript == another.superscript: 
            return True
        else : 
            return False
    def __lt__(self, another):
        if self.subscript < another.subscript:
            return True
        elif self.subscript > another.subscript:
            return False
        elif self.superscript < another.superscript:
            return True
        else: return False
    def isEmpty(self):
        if self.subscript == [] and self.superscript == []:
            return True
        else :
            return False
    def canonicalize(self):
        if self.subscript[0].index > self.superscript[0].index:
            self.subscript,self.superscript = self.superscript,self.subscript

class Tensor():
    def __init__(self,coefficient = Fraction(1,1),labels = [], permutation = [],reusable = False,id = 0):
        self.coefficient = coefficient
        self.labels =  labels 
        self.permutation = permutation
        self.reusable = reusable
        self.id = id
 
    def __repr__(self):
        latexstring = "("
        if self.reusable:
            latexstring += "A_" + str(self.id) + ")_{"
        else:
            latexstring += "B_" + str(self.id) + ")_{" 
        for item in self.labels[:len(self.labels)//2]:
            latexstring += item.showwithoutDagger()
        latexstring += "}^{"
        for item in self.labels[len(self.labels)//2:]:
            latexstring += item.showwithoutDagger()
        latexstring += "}"
        return latexstring
    
    def getid(self):
        return self.id

    def duplicate(self):
        return Tensor(self.coefficient,deepcopy(self.labels),deepcopy(self.permutation),self.reusable,self.id)
    
    def swap(self, originallist, targetlist):
        tmp = self.duplicate()
        for i in range(len(tmp.labels)):
            if tmp.labels[i] in originallist:
                tmp.labels[i] = targetlist[originallist.index(tmp.labels[i])]
        return tmp

#    def getLabels(self):
#       if (len(self.contents[0].amplitude) == 1):
#           self.labels = self.contents[0].amplitude[0][0].subscript + self.contents[0].amplitude[0][0].superscript
#           self.labels.sort()
#       else:
#           labels = self.contents[0].amplitude[0][0].subscript + self.contents[0].amplitude[0][0].superscript
#           for i in range(1,len(self.contents[0].amplitude)) :
#               nextlabel = self.contents[0].amplitude[i][0].subscript + self.contents[0].amplitude[i][0].superscript
#               sharedlabel = [item for item in labels if item in nextlabel]
#               labels = [item for item in labels if item not in sharedlabel] + \
#                   [item for item in nextlabel if item not in sharedlabel]
#           self.labels = labels
#           self.labels.sort()
#   def isFullyFactorized(self):
#       for tensors in self.contents:
#           for tensor in tensors:
#               if tensor.maxlength() > 2:#use Tensor.maxlength() or OperatorStr.maxlength()
#                   return False
#       return True
#   def maxlength(self):
#       return max([len(item) for item in self.contents])
#   def factorize(self):
#       if not self.isFullyFactorized():
#           pass
#   def hasSameContents(self, another):
#       if len(self.contents) == len(another.contents):
#           for i in range(len(self.contents)):
#               if self.contents[i][0] != another.contents[i][0]:
#                   return False
#           return True
#       return False
#    def factorizablewith(self,another):
#        selflen = len(self)
#        anotherlen = len(another)
#        if selflen == 1 and anotherlen == 1:
#            pass
#        for selftensor in self.contents:
#            for anothertensor in another.contents:
#                if type(selftensor) == type(anothertensor) and selftensor == anothertensor:
#                    return selftensor
#        return False
#    def factorize(self):
#        pass
class BinaryTensorContraction():
    def __init__(self,coefficient = Fraction(1,1), permutations = [],tensors = []):
        self.coefficient = coefficient
        self.permutations = permutations
        self.tensors = tensors

     
class TensorExpression():
    def __init__(self,labels = [],tensors = [], id = 0, reusable = False):
        #suppose tensors is a nested list of tensors
        self.labels = labels
        self.tensors = tensors
        self.id = id
        self.reusable = reusable  

class TensorExpressionList():
    def __init__(self,tel = []):
        self.tel = tel


class OperationTree():
    def __init__(self, children = [], factorizable = [], unfactorizable = []):#chilren is either empty or a list of operation trees.
        self.children = children
        self.factorizable = factorizable
        self.unfactorizable = unfactorizable
    def duplicate(self):
        return OperationTree(children = deepcopy(self.children), factorizable = deepcopy(self.factorizable), unfactorizable = deepcopy(self.unfactorizable))
    def doSingleFactorization(self):
        pass
    def factorize(self,iteration = 1, order = 0):
        if iteration == 1:
            nfactorizable = len(self.factorizable)
            matched = {}
            commonamplitude = []
            alreadyfactorized = []
            for i in range(nfactorizable):
                for j in range(i+1,nfactorizable):
                    if j not in alreadyfactorized:
                        if len(self.factorizable[i].amplitude) > 1 and len(self.factorizable[j].amplitude) > 1:
                            if self.factorizable[i].amplitude[-1] == self.factorizable[j].amplitude[-1]:
                                alreadyfactorized.append(j)
                                alreadyfactorized.append(i)
                                if i not in matched:
                                    matched[i] = [j]
                                else:
                                    matched[i].append(j)
                            elif self.factorizable[i].permutation or self.factorizable[j].permutation:
                                if len(self.factorizable[i].permutation) >= len(self.factorizable[j].permutation):
                                    for ipermutation in self.factorizable[i].permutation:
                                        originalorder = ipermutation[0].subscript + ipermutation[0].superscript
                                        permutedorder = deepcopy(originalorder)
                                        permutedorder.reverse()
                                        icopy = self.factorizable[i].duplicate()
                                        icopy = deepcopy(icopy.swap(originalorder,permutedorder))
                                        if icopy.amplitude[-1] == self.factorizable[j].amplitude[-1]:
                                            icopy.coefficient *= -1
                                            self.factorizable[i] = icopy.duplicate()
                                            alreadyfactorized.append(j)
                                            alreadyfactorized.append(i)
                                            if i not in matched:
                                                matched[i] = [j]
                                            else:
                                                matched[i].append(j)
                                elif len(self.factorizable[i].permutation) <= len(self.factorizable[j].permutation):
                                    for jpermutation in self.factorizable[j].permutation:
                                        originalorder = jpermutation[0].subscript + jpermutation[0].superscript
                                        permutedorder = deepcopy(originalorder)
                                        permutedorder.reverse()
                                        jcopy = self.factorizable[j].duplicate()
                                        jcopy = deepcopy(jcopy.swap(originalorder,permutedorder))
                                        if jcopy.amplitude[-1] == self.factorizable[i].amplitude[-1]:
                                            jcopy.coefficient *= -1
                                            self.factorizable[j] = jcopy.duplicate()
                                            alreadyfactorized.append(j)
                                            alreadyfactorized.append(i)
                                            if i not in matched:
                                                matched[i] = [j]
                                            else:
                                                matched[i].append(j)
            self.unfactorizable = [self.factorizable[i] for i in range(len(self.factorizable)) if i not in alreadyfactorized ]
            if matched:
                keys = list(matched)
                for i in range(len(keys)):
                    for j in matched[keys[i]]:
                        if self.factorizable[keys[i]].amplitude[-1] != self.factorizable[j].amplitude[-1]:
                            if self.factorizable[j].permutation:
                                for jpermutation in self.factorizable[j].permutation:
                                    originalorder = jpermutation[0].subscript + jpermutation[0].superscript
                                    permutedorder = deepcopy(originalorder)
                                    permutedorder.reverse()
                                    jcopy = self.factorizable[j].duplicate()
                                    jcopy = deepcopy(jcopy.swap(originalorder,permutedorder))
                                    if jcopy.amplitude[-1] == self.factorizable[keys[i]].amplitude[-1]:
                                        jcopy.coefficient *= -1
                                        self.factorizable[j] = jcopy.duplicate()
                                        break
                #Factorize permutation operators
                commonpermutations = []
                for i in range(len(keys)):
                    if self.factorizable[keys[i]].permutation:
                        supposealltrue = [True]*len(self.factorizable[keys[i]].permutation)
                        lastamplitudelables = self.factorizable[keys[i]].amplitude[-1][0].subscript + \
                            self.factorizable[keys[i]].amplitude[-1][0].superscript
                        for k in range(len(self.factorizable[keys[i]].permutation)):
                            if self.factorizable[keys[i]].permutation[k][0].subscript[0] not in lastamplitudelables \
                                and self.factorizable[keys[i]].permutation[k][0].superscript[0] not in lastamplitudelables:
                                supposealltrue[k] = False
                        for j in matched[keys[i]]:
                            for k in range(len(self.factorizable[keys[i]].permutation)):
                                if self.factorizable[keys[i]].permutation[k] not in self.factorizable[j].permutation:
                                    supposealltrue[k] = False
                        tmppermutations = []
                        for k in range(len(self.factorizable[keys[i]].permutation)):
                            if supposealltrue[k]:
                                tmppermutations += self.factorizable[keys[i]].permutation[k]
                        commonpermutations.append(tmppermutations)
                    else:
                        commonpermutations.append([])
                    if commonpermutations[i]:
                        for item in commonpermutations[i]:
                            self.factorizable[keys[i]].permutation.remove([item])
                            for j in matched[keys[i]]:
                                self.factorizable[j].permutation.remove([item])
                for i in range(len(keys)):
                    commonamplitude.append(self.factorizable[keys[i]].amplitude[-1])
                for k,v in matched.items():
                    tmplist = v + [k]
                    tmpoperationtree = deepcopy(OperationTree())
                    for num in tmplist:
                        del self.factorizable[num].amplitude[-1]
                        tmpoperationtree.factorizable.append(deepcopy(self.factorizable[num].duplicate()))
                    self.children.append(tmpoperationtree.duplicate())
                for i in range(len(keys)):
                    index = keys[i]
                    if len(self.factorizable[index].amplitude) == 1:
                        label = self.factorizable[index].amplitude[0][0].subscript + \
                            self.factorizable[index].amplitude[0][0].superscript
                        commonamplitude[i].insert(0,Tensor(labels = label, id = i+1 + iteration*10))
                        if commonpermutations[i]:
                            commonamplitude[i].insert(0,commonpermutations[i])
                    else:
                        label = self.factorizable[index].amplitude[0][0].subscript + \
                            self.factorizable[index].amplitude[0][0].superscript
                        
                        for j in range(1,len(self.factorizable[index].amplitude)):
                            nextlabel = self.factorizable[index].amplitude[j][0].subscript + \
                                 self.factorizable[index].amplitude[j][0].superscript
                            sharedlabel = [item for item in label if item in nextlabel]
                            label = [item for item in label if item not in sharedlabel] + \
                                [item for item in nextlabel if item not in sharedlabel]
                            commonamplitude[i].insert(0,Tensor(labels = label, id = i+1 + iteration*10))
                            if commonpermutations[i]:
                                commonamplitude[i].insert(0,commonpermutations[i])
                self.factorizable = deepcopy(commonamplitude)

                for i in range(len(keys)):
                    self.children[i].factorize(iteration+1, i+1) 
        else:
#            print(iteration)
#            print(order)
#            print(self.factorizable)
            nfactorizable = len(self.factorizable)
            matched = {}
            commonamplitude = []
            alreadyfactorized = []
            for i in range(nfactorizable):
                for j in range(i+1,nfactorizable):
                    if j not in alreadyfactorized:
                        if len(self.factorizable[i].amplitude) > 0 and len(self.factorizable[j].amplitude) > 0:
                            if self.factorizable[i].amplitude[-1] == self.factorizable[j].amplitude[-1]:
                                alreadyfactorized.append(j)
                                alreadyfactorized.append(i)
                                if i not in matched:
                                    matched[i] = [j]
                                else:
                                    matched[i].append(j)
                            elif self.factorizable[i].permutation or self.factorizable[j].permutation:
                                if len(self.factorizable[i].permutation) >= len(self.factorizable[j].permutation):
                                    for ipermutation in self.factorizable[i].permutation:
                                        originalorder = ipermutation[0].subscript + ipermutation[0].superscript
                                        permutedorder = deepcopy(originalorder)
                                        permutedorder.reverse()
                                        icopy = self.factorizable[i].duplicate()
                                        icopy = deepcopy(icopy.swap(originalorder,permutedorder))
                                        if icopy.amplitude[-1] == self.factorizable[j].amplitude[-1]:
                                            icopy.coefficient *= -1
                                            self.factorizable[i] = icopy.duplicate()
                                            alreadyfactorized.append(j)
                                            alreadyfactorized.append(i)
                                            if i not in matched:
                                                matched[i] = [j]
                                            else:
                                                matched[i].append(j)
                                elif len(self.factorizable[i].permutation) <= len(self.factorizable[j].permutation):
                                    for jpermutation in self.factorizable[j].permutation:
                                        originalorder = jpermutation[0].subscript + jpermutation[0].superscript
                                        permutedorder = deepcopy(originalorder)
                                        permutedorder.reverse()
                                        jcopy = self.factorizable[j].duplicate()
                                        jcopy = deepcopy(jcopy.swap(originalorder,permutedorder))
                                        if jcopy.amplitude[-1] == self.factorizable[i].amplitude[-1]:
                                            jcopy.coefficient *= -1
                                            self.factorizable[j] = jcopy.duplicate()
                                            alreadyfactorized.append(j)
                                            alreadyfactorized.append(i)
                                            if i not in matched:
                                                matched[i] = [j]
                                            else:
                                                matched[i].append(j)
            self.unfactorizable = [self.factorizable[i] for i in range(len(self.factorizable)) if i not in alreadyfactorized ]
            if matched:
                keys = list(matched)
                for i in range(len(keys)):
                    for j in matched[keys[i]]:
                        if self.factorizable[keys[i]].amplitude[-1] != self.factorizable[j].amplitude[-1]:
                            if self.factorizable[j].permutation:
                                for jpermutation in self.factorizable[j].permutation:
                                    originalorder = jpermutation[0].subscript + jpermutation[0].superscript
                                    permutedorder = deepcopy(originalorder)
                                    permutedorder.reverse()
                                    jcopy = self.factorizable[j].duplicate()
                                    jcopy = deepcopy(jcopy.swap(originalorder,permutedorder))
                                    if jcopy.amplitude[-1] == self.factorizable[keys[i]].amplitude[-1]:
                                        jcopy.coefficient *= -1
                                        self.factorizable[j] = jcopy.duplicate()
                                        break
                #Factorize permutation operators
                commonpermutations = []
                for i in range(len(keys)):
                    if self.factorizable[keys[i]].permutation:
                        supposealltrue = [True]*len(self.factorizable[keys[i]].permutation)
                        lastamplitudelables = self.factorizable[keys[i]].amplitude[-1][0].subscript + \
                            self.factorizable[keys[i]].amplitude[-1][0].superscript
                        for k in range(len(self.factorizable[keys[i]].permutation)):
                            if self.factorizable[keys[i]].permutation[k][0].subscript[0] not in lastamplitudelables \
                                and self.factorizable[keys[i]].permutation[k][0].superscript[0] not in lastamplitudelables:
                                supposealltrue[k] = False
                        for j in matched[keys[i]]:
                            for k in range(len(self.factorizable[keys[i]].permutation)):
                                if self.factorizable[keys[i]].permutation[k] not in self.factorizable[j].permutation:
                                    supposealltrue[k] = False
                        tmppermutations = []
                        for k in range(len(self.factorizable[keys[i]].permutation)):
                            if supposealltrue[k]:
                                tmppermutations += self.factorizable[keys[i]].permutation[k]
                        commonpermutations.append(tmppermutations)
                    else:
                        commonpermutations.append([])
                    if commonpermutations[i]:
                        for item in commonpermutations[i]:
                            self.factorizable[keys[i]].permutation.remove([item])
                            for j in matched[keys[i]]:
                                self.factorizable[j].permutation.remove([item])
                for i in range(len(keys)):
                    commonamplitude.append(self.factorizable[keys[i]].amplitude[-1])
                for k,v in matched.items():
                    tmplist = v + [k]
                    tmpoperationtree = deepcopy(OperationTree())
                    for num in tmplist:
                        del self.factorizable[num].amplitude[-1]
                        tmpoperationtree.factorizable.append(deepcopy(self.factorizable[num].duplicate()))
                    self.children.append(tmpoperationtree.duplicate())
                for i in range(len(keys)):
                    index = keys[i]
                    if len(self.factorizable[index].amplitude) == 1:
                        label = self.factorizable[index].amplitude[0][0].subscript + \
                            self.factorizable[index].amplitude[0][0].superscript
                        commonamplitude[i].insert(0,Tensor(labels = label, id = order*10**(iteration-1) + i))
                        if commonpermutations[i]:
                            commonamplitude[i].insert(0,commonpermutations[i])
                    else:
                        label = self.factorizable[index].amplitude[0][0].subscript + \
                            self.factorizable[index].amplitude[0][0].superscript
                        
                        for j in range(1,len(self.factorizable[index].amplitude)):
                            nextlabel = self.factorizable[index].amplitude[j][0].subscript + \
                                 self.factorizable[index].amplitude[j][0].superscript
                            sharedlabel = [item for item in label if item in nextlabel]
                            label = [item for item in label if item not in sharedlabel] + \
                                [item for item in nextlabel if item not in sharedlabel]
                            commonamplitude[i].insert(0,Tensor(labels = label, id = order*10**(iteration-1) + i))
                            if commonpermutations[i]:
                                commonamplitude[i].insert(0,commonpermutations[i])
                self.factorizable = deepcopy(commonamplitude)
                for i in range(len(keys)):
                    self.children[i].factorize(iteration + 1, i+1) 
            else:
                return       

    def factorizetest(self,iteration = 1, order = 0):
        nfactorizable = len(self.factorizable)
        matched = {}
        commonamplitude = []
        alreadyfactorized = []
        for i in range(nfactorizable):
            if i not in alreadyfactorized:
                for j in range(i+1,nfactorizable):
                    if j not in alreadyfactorized:
                        if len(self.factorizable[i].amplitude) > 1 and len(self.factorizable[j].amplitude) > 1:
                            if self.factorizable[i].amplitude[-1] == self.factorizable[j].amplitude[-1]:
                                if i not in alreadyfactorized:
                                    alreadyfactorized.append(i)
                                alreadyfactorized.append(j)
                                if i not in matched:
                                    matched[i] = [j]
                                else:
                                    matched[i].append(j)
                            elif self.factorizable[i].permutation or self.factorizable[j].permutation:
                                if len(self.factorizable[i].permutation) == len(self.factorizable[j].permutation):
                                    isummationindexes = []
                                    iinternalplist = []
                                    iinternalhlist = []
                                    if self.factorizable[i].summation:
                                        isummationindexes = self.factorizable[i].summation[0][0].indexes
                                    if isummationindexes:
                                        iinternalplist = [op for op in isummationindexes if op.type == "p"]
                                        iinternalhlist = [op for op in isummationindexes if op.type == "h"]
                                    jsummationindexes = []
                                    jinternalplist = []
                                    jinternalhlist = []
                                    if self.factorizable[j].summation:
                                        jsummationindexes = self.factorizable[j].summation[0][0].indexes
                                    if jsummationindexes:
                                        jinternalplist = [op for op in jsummationindexes if op.type == "p"]
                                        jinternalhlist = [op for op in jsummationindexes if op.type == "h"]
                                    if len(iinternalhlist) //2 + len(iinternalplist)//2 >= \
                                        len(jinternalhlist) //2 + len(jinternalplist)//2:
                                        if len(iinternalplist) == 2:
                                            icopy = deepcopy(self.factorizable[i].duplicate())
                                            icopy = deepcopy(jcopy.swap(iinternalplist,iinternalplist[::-1]))
                                            if icopy.amplitude[-1] == self.factorizable[j].amplitude[-1]:
                                                icopy.coefficient *= -1
                                                self.factorizable[i] = icopy.duplicate()
                                                if i not in alreadyfactorized:
                                                    alreadyfactorized.append(i)
                                                alreadyfactorized.append(j)
                                                if i not in matched:
                                                    matched[i] = [j]
                                                else:
                                                    matched[i].append(j)
                                            if j not in alreadyfactorized:
                                                for ipermutation in self.factorizable[i].permutation:
                                                    originalorder = ipermutation[0].subscript + ipermutation[0].superscript
                                                    permutedorder = deepcopy(originalorder)
                                                    permutedorder.reverse()
                                                    icopy = self.factorizable[i].duplicate()
                                                    icopy = deepcopy(icopy.swap(originalorder,permutedorder))
                                                    icopy = deepcopy(icopy.swap(iinternalplist,iinternalplist[::-1]))
                                                    if icopy.amplitude[-1] == self.factorizable[j].amplitude[-1]:
                                                        self.factorizable[i] = icopy.duplicate()
                                                        if i not in alreadyfactorized:
                                                            alreadyfactorized.append(i)
                                                        alreadyfactorized.append(j)
                                                        if i not in matched:
                                                            matched[i] = [j]
                                                        else:
                                                            matched[i].append(j)
                                        if j not in alreadyfactorized and len(iinternalhlist) == 2:
                                            icopy = deepcopy(self.factorizable[i].duplicate())
                                            icopy = deepcopy(icopy.swap(iinternalhlist,iinternalhlist[::-1]))
                                            if icopy.amplitude[-1] == self.factorizable[j].amplitude[-1]:
                                                icopy.coefficient *= -1
                                                self.factorizable[i] = icopy.duplicate()
                                                if i not in alreadyfactorized:
                                                    alreadyfactorized.append(i)
                                                alreadyfactorized.append(j)
                                                if i not in matched:
                                                    matched[i] = [j]
                                                else:
                                                    matched[i].append(j)
                                            for ipermutation in self.factorizable[i].permutation:
                                                originalorder = ipermutation[0].subscript + ipermutation[0].superscript
                                                permutedorder = deepcopy(originalorder)
                                                permutedorder.reverse()
                                                icopy = self.factorizable[i].duplicate()
                                                icopy = deepcopy(icopy.swap(originalorder,permutedorder))
                                                icopy = deepcopy(icopy.swap(iinternalhlist,iinternalhlist[::-1]))
                                                if icopy.amplitude[-1] == self.factorizable[j].amplitude[-1]:
                                                    self.factorizable[i] = icopy.duplicate()
                                                    if i not in alreadyfactorized:
                                                        alreadyfactorized.append(i)
                                                    alreadyfactorized.append(j)
                                                    if i not in matched:
                                                        matched[i] = [j]
                                                    else:
                                                        matched[i].append(j)
                                    else:
                                        if len(jinternalplist) == 2:
                                            jcopy = deepcopy(self.factorizable[j].duplicate())
                                            jcopy = deepcopy(jcopy.swap(jinternalplist,jinternalplist[::-1]))
                                            if jcopy.amplitude[-1] == self.factorizable[i].amplitude[-1]:
                                                jcopy.coefficient *= -1
                                                self.factorizable[j] = jcopy.duplicate()
                                                if i not in alreadyfactorized:
                                                    alreadyfactorized.append(i)
                                                alreadyfactorized.append(j)
                                                if i not in matched:
                                                    matched[i] = [j]
                                                else:
                                                    matched[i].append(j)
                                            if j not in alreadyfactorized:
                                                for jpermutation in self.factorizable[j].permutation:
                                                    originalorder = jpermutation[0].subscript + jpermutation[0].superscript
                                                    permutedorder = deepcopy(originalorder)
                                                    permutedorder.reverse()
                                                    jcopy = self.factorizable[j].duplicate()
                                                    jcopy = deepcopy(jcopy.swap(originalorder,permutedorder))
                                                    jcopy = deepcopy(jcopy.swap(jinternalplist,jinternalplist[::-1]))
                                                    if jcopy.amplitude[-1] == self.factorizable[i].amplitude[-1]:
                                                        self.factorizable[j] = jcopy.duplicate()
                                                        if i not in alreadyfactorized:
                                                            alreadyfactorized.append(i)
                                                        alreadyfactorized.append(j)
                                                        if i not in matched:
                                                            matched[i] = [j]
                                                        else:
                                                            matched[i].append(j)
                                        if j not in alreadyfactorized and len(jinternalhlist) == 2:
                                            jcopy = deepcopy(self.factorizable[j].duplicate())
                                            jcopy = deepcopy(jcopy.swap(jinternalhlist,jinternalhlist[::-1]))
                                            if jcopy.amplitude[-1] == self.factorizable[i].amplitude[-1]:
                                                jcopy.coefficient *= -1
                                                self.factorizable[j] = jcopy.duplicate()
                                                if i not in alreadyfactorized:
                                                    alreadyfactorized.append(i)
                                                alreadyfactorized.append(j)
                                                if i not in matched:
                                                    matched[i] = [j]
                                                else:
                                                    matched[i].append(j)
                                            if j not in alreadyfactorized:
                                                for jpermutation in self.factorizable[j].permutation:
                                                    originalorder = jpermutation[0].subscript + jpermutation[0].superscript
                                                    permutedorder = deepcopy(originalorder)
                                                    permutedorder.reverse()
                                                    jcopy = self.factorizable[j].duplicate()
                                                    jcopy = deepcopy(jcopy.swap(originalorder,permutedorder))
                                                    jcopy = deepcopy(jcopy.swap(jinternalhlist,jinternalhlist[::-1]))
                                                    if jcopy.amplitude[-1] == self.factorizable[i].amplitude[-1]:
                                                        self.factorizable[j] = jcopy.duplicate()
                                                        if i not in alreadyfactorized:
                                                            alreadyfactorized.append(i)
                                                        alreadyfactorized.append(j)
                                                        if i not in matched:
                                                            matched[i] = [j]
                                                        else:
                                                            matched[i].append(j)                                  
                                if len(self.factorizable[i].permutation) >= len(self.factorizable[j].permutation):
                                    for ipermutation in self.factorizable[i].permutation:
                                        originalorder = ipermutation[0].subscript + ipermutation[0].superscript
                                        permutedorder = deepcopy(originalorder)
                                        permutedorder.reverse()
                                        icopy = self.factorizable[i].duplicate()
                                        icopy = deepcopy(icopy.swap(originalorder,permutedorder))
                                        if icopy.amplitude[-1] == self.factorizable[j].amplitude[-1]:
                                            icopy.coefficient *= -1
                                            self.factorizable[i] = icopy.duplicate()
                                            if i not in alreadyfactorized:
                                                alreadyfactorized.append(i)
                                            alreadyfactorized.append(j)
                                            if i not in matched:
                                                matched[i] = [j]
                                            else:
                                                matched[i].append(j)
                                    if j not in alreadyfactorized:
                                        isummationindexes = []
                                        iinternalplist = []
                                        iinternalhlist = []
                                        if self.factorizable[i].summation:
                                            isummationindexes = self.factorizable[i].summation[0][0].indexes
                                        if isummationindexes:
                                            iinternalplist = [op for op in isummationindexes if op.type == "p"]
                                            iinternalhlist = [op for op in isummationindexes if op.type == "h"]
                                        if len(iinternalplist) == 2:
                                            icopy = deepcopy(self.factorizable[i].duplicate())
                                            icopy = deepcopy(jcopy.swap(iinternalplist,iinternalplist[::-1]))
                                            if icopy.amplitude[-1] == self.factorizable[j].amplitude[-1]:
                                                icopy.coefficient *= -1
                                                self.factorizable[i] = icopy.duplicate()
                                                if i not in alreadyfactorized:
                                                    alreadyfactorized.append(i)
                                                alreadyfactorized.append(j)
                                                if i not in matched:
                                                    matched[i] = [j]
                                                else:
                                                    matched[i].append(j)
                                            if j not in alreadyfactorized:
                                                for ipermutation in self.factorizable[i].permutation:
                                                    originalorder = ipermutation[0].subscript + ipermutation[0].superscript
                                                    permutedorder = deepcopy(originalorder)
                                                    permutedorder.reverse()
                                                    icopy = self.factorizable[i].duplicate()
                                                    icopy = deepcopy(icopy.swap(originalorder,permutedorder))
                                                    icopy = deepcopy(icopy.swap(iinternalplist,iinternalplist[::-1]))
                                                    if icopy.amplitude[-1] == self.factorizable[j].amplitude[-1]:
                                                        self.factorizable[i] = icopy.duplicate()
                                                        if i not in alreadyfactorized:
                                                            alreadyfactorized.append(i)
                                                        alreadyfactorized.append(j)
                                                        if i not in matched:
                                                            matched[i] = [j]
                                                        else:
                                                            matched[i].append(j)
                                        if j not in alreadyfactorized and len(iinternalhlist) == 2:
                                            icopy = deepcopy(self.factorizable[i].duplicate())
                                            icopy = deepcopy(icopy.swap(iinternalhlist,iinternalhlist[::-1]))
                                            if icopy.amplitude[-1] == self.factorizable[j].amplitude[-1]:
                                                icopy.coefficient *= -1
                                                self.factorizable[i] = icopy.duplicate()
                                                if i not in alreadyfactorized:
                                                    alreadyfactorized.append(i)
                                                alreadyfactorized.append(j)
                                                if i not in matched:
                                                    matched[i] = [j]
                                                else:
                                                    matched[i].append(j)
                                            for ipermutation in self.factorizable[i].permutation:
                                                originalorder = ipermutation[0].subscript + ipermutation[0].superscript
                                                permutedorder = deepcopy(originalorder)
                                                permutedorder.reverse()
                                                icopy = self.factorizable[i].duplicate()
                                                icopy = deepcopy(icopy.swap(originalorder,permutedorder))
                                                icopy = deepcopy(icopy.swap(iinternalhlist,iinternalhlist[::-1]))
                                                if icopy.amplitude[-1] == self.factorizable[j].amplitude[-1]:
                                                    self.factorizable[i] = icopy.duplicate()
                                                    if i not in alreadyfactorized:
                                                        alreadyfactorized.append(i)
                                                    alreadyfactorized.append(j)
                                                    if i not in matched:
                                                        matched[i] = [j]
                                                    else:
                                                        matched[i].append(j)
                                elif len(self.factorizable[i].permutation) <= len(self.factorizable[j].permutation):
                                    for jpermutation in self.factorizable[j].permutation:
                                        originalorder = jpermutation[0].subscript + jpermutation[0].superscript
                                        permutedorder = deepcopy(originalorder)
                                        permutedorder.reverse()
                                        jcopy = self.factorizable[j].duplicate()
                                        jcopy = deepcopy(jcopy.swap(originalorder,permutedorder))
                                        if jcopy.amplitude[-1] == self.factorizable[i].amplitude[-1]:
                                            jcopy.coefficient *= -1
                                            self.factorizable[j] = jcopy.duplicate()
                                            if i not in alreadyfactorized:
                                                alreadyfactorized.append(i)
                                            alreadyfactorized.append(j)
                                            if i not in matched:
                                                matched[i] = [j]
                                            else:
                                                matched[i].append(j)
                                    if j not in alreadyfactorized:
                                        jsummationindexes = []
                                        jinternalplist = []
                                        jinternalhlist = []
                                        if self.factorizable[j].summation:
                                            jsummationindexes = self.factorizable[j].summation[0][0].indexes
                                        if jsummationindexes:
                                            jinternalplist = [op for op in jsummationindexes if op.type == "p"]
                                            jinternalhlist = [op for op in jsummationindexes if op.type == "h"]
                                        if len(jinternalplist) == 2:
                                            jcopy = deepcopy(self.factorizable[j].duplicate())
                                            jcopy = deepcopy(jcopy.swap(jinternalplist,jinternalplist[::-1]))
                                            if jcopy.amplitude[-1] == self.factorizable[i].amplitude[-1]:
                                                jcopy.coefficient *= -1
                                                self.factorizable[j] = jcopy.duplicate()
                                                if i not in alreadyfactorized:
                                                    alreadyfactorized.append(i)
                                                alreadyfactorized.append(j)
                                                if i not in matched:
                                                    matched[i] = [j]
                                                else:
                                                    matched[i].append(j)
                                            if i not in alreadyfactorized:
                                                for jpermutation in self.factorizable[j].permutation:
                                                    originalorder = jpermutation[0].subscript + jpermutation[0].superscript
                                                    permutedorder = deepcopy(originalorder)
                                                    permutedorder.reverse()
                                                    jcopy = self.factorizable[j].duplicate()
                                                    jcopy = deepcopy(jcopy.swap(originalorder,permutedorder))
                                                    jcopy = deepcopy(jcopy.swap(jinternalplist,jinternalplist[::-1]))
                                                    if jcopy.amplitude[-1] == self.factorizable[i].amplitude[-1]:
                                                        self.factorizable[j] = jcopy.duplicate()
                                                        if i not in alreadyfactorized:
                                                            alreadyfactorized.append(i)
                                                        alreadyfactorized.append(j)
                                                        if i not in matched:
                                                            matched[i] = [j]
                                                        else:
                                                            matched[i].append(j)
                                        if j not in alreadyfactorized and len(jinternalhlist) == 2:
                                            jcopy = deepcopy(self.factorizable[j].duplicate())
                                            jcopy = deepcopy(jcopy.swap(jinternalhlist,jinternalhlist[::-1]))
                                            if jcopy.amplitude[-1] == self.factorizable[i].amplitude[-1]:
                                                jcopy.coefficient *= -1
                                                self.factorizable[j] = jcopy.duplicate()
                                                if i not in alreadyfactorized:
                                                    alreadyfactorized.append(i)
                                                alreadyfactorized.append(j)
                                                if i not in matched:
                                                    matched[i] = [j]
                                                else:
                                                    matched[i].append(j)
                                            if j not in alreadyfactorized:
                                                for jpermutation in self.factorizable[j].permutation:
                                                    originalorder = jpermutation[0].subscript + jpermutation[0].superscript
                                                    permutedorder = deepcopy(originalorder)
                                                    permutedorder.reverse()
                                                    jcopy = self.factorizable[j].duplicate()
                                                    jcopy = deepcopy(jcopy.swap(originalorder,permutedorder))
                                                    jcopy = deepcopy(jcopy.swap(jinternalhlist,jinternalhlist[::-1]))
                                                    if jcopy.amplitude[-1] == self.factorizable[i].amplitude[-1]:
                                                        self.factorizable[j] = jcopy.duplicate()
                                                        if i not in alreadyfactorized:
                                                            alreadyfactorized.append(i)
                                                        alreadyfactorized.append(j)
                                                        if i not in matched:
                                                            matched[i] = [j]
                                                        else:
                                                            matched[i].append(j) 
                            elif self.factorizable[i].summation or self.factorizable[j].summation:
                                    isummationindexes = []
                                    iinternalplist = []
                                    iinternalhlist = []
                                    if self.factorizable[i].summation:
                                        isummationindexes = self.factorizable[i].summation[0][0].indexes
                                    if isummationindexes:
                                        iinternalplist = [op for op in isummationindexes if op.type == "p"]
                                        iinternalhlist = [op for op in isummationindexes if op.type == "h"]
                                    jsummationindexes = []
                                    jinternalplist = []
                                    jinternalhlist = []
                                    if self.factorizable[j].summation:
                                        jsummationindexes = self.factorizable[j].summation[0][0].indexes
                                    if jsummationindexes:
                                        jinternalplist = [op for op in jsummationindexes if op.type == "p"]
                                        jinternalhlist = [op for op in jsummationindexes if op.type == "h"]
                                    if len(iinternalhlist) //2 + len(iinternalplist)//2 >= \
                                        len(jinternalhlist) //2 + len(jinternalplist)//2:
                                        if len(iinternalplist) == 2:
                                            icopy = deepcopy(self.factorizable[i].duplicate())
                                            icopy = deepcopy(jcopy.swap(iinternalplist,iinternalplist[::-1]))
                                            if icopy.amplitude[-1] == self.factorizable[j].amplitude[-1]:
                                                icopy.coefficient *= -1
                                                self.factorizable[i] = icopy.duplicate()
                                                if i not in alreadyfactorized:
                                                    alreadyfactorized.append(i)
                                                alreadyfactorized.append(j)
                                                if i not in matched:
                                                    matched[i] = [j]
                                                else:
                                                    matched[i].append(j)
                                        if j not in alreadyfactorized and len(iinternalhlist) == 2:
                                            icopy = deepcopy(self.factorizable[i].duplicate())
                                            icopy = deepcopy(icopy.swap(iinternalhlist,iinternalhlist[::-1]))
                                            if icopy.amplitude[-1] == self.factorizable[j].amplitude[-1]:
                                                icopy.coefficient *= -1
                                                self.factorizable[i] = icopy.duplicate()
                                                if i not in alreadyfactorized:
                                                    alreadyfactorized.append(i)
                                                alreadyfactorized.append(j)
                                                if i not in matched:
                                                    matched[i] = [j]
                                                else:
                                                    matched[i].append(j)
                                    else:
                                        if len(jinternalplist) == 2:
                                            jcopy = deepcopy(self.factorizable[j].duplicate())
                                            jcopy = deepcopy(jcopy.swap(jinternalplist,jinternalplist[::-1]))
                                            if jcopy.amplitude[-1] == self.factorizable[i].amplitude[-1]:
                                                jcopy.coefficient *= -1
                                                self.factorizable[j] = jcopy.duplicate()
                                                if i not in alreadyfactorized:
                                                    alreadyfactorized.append(i)
                                                alreadyfactorized.append(j)
                                                if i not in matched:
                                                    matched[i] = [j]
                                                else:
                                                    matched[i].append(j)
                                        if j not in alreadyfactorized and len(jinternalhlist) == 2:
                                            jcopy = deepcopy(self.factorizable[j].duplicate())
                                            jcopy = deepcopy(jcopy.swap(jinternalhlist,jinternalhlist[::-1]))
                                            if jcopy.amplitude[-1] == self.factorizable[i].amplitude[-1]:
                                                jcopy.coefficient *= -1
                                                self.factorizable[j] = jcopy.duplicate()
                                                if i not in alreadyfactorized:
                                                    alreadyfactorized.append(i)
                                                alreadyfactorized.append(j)
                                                if i not in matched:
                                                    matched[i] = [j]
                                                else:
                                                    matched[i].append(j)    
                                        
        self.unfactorizable = [self.factorizable[i] for i in range(len(self.factorizable)) if i not in alreadyfactorized ]
        if matched:
            keys = list(matched)
            for i in range(len(keys)):
                for j in matched[keys[i]]:
                    if self.factorizable[keys[i]].amplitude[-1] != self.factorizable[j].amplitude[-1]:
                        if self.factorizable[j].permutation:
                            for jpermutation in self.factorizable[j].permutation:
                                originalorder = jpermutation[0].subscript + jpermutation[0].superscript
                                permutedorder = deepcopy(originalorder)
                                permutedorder.reverse()
                                jcopy = self.factorizable[j].duplicate()
                                jcopy = deepcopy(jcopy.swap(originalorder,permutedorder))
                                if jcopy.amplitude[-1] == self.factorizable[keys[i]].amplitude[-1]:
                                    jcopy.coefficient *= -1
                                    self.factorizable[j] = jcopy.duplicate()
                                    break
                lastamplitudelables = self.factorizable[keys[i]].amplitude[-1][0].subscript + \
                        self.factorizable[keys[i]].amplitude[-1][0].superscript
                if self.factorizable[keys[i]].summation:
                    index_to_be_deleted = []
                    for k in range(len(self.factorizable[keys[i]].summation[0][0].indexes)):
                        if self.factorizable[keys[i]].summation[0][0].indexes[k] in lastamplitudelables:
                            index_to_be_deleted.append(k)
                    if index_to_be_deleted:
                        for k in sorted(index_to_be_deleted, reverse=True):
                            del self.factorizable[keys[i]].summation[0][0].indexes[k]
                for j in matched[keys[i]]:
                    index_to_be_deleted = []
                    for k in range(len(self.factorizable[j].summation[0][0].indexes)):
                        if self.factorizable[j].summation[0][0].indexes[k] in lastamplitudelables:
                            index_to_be_deleted.append(k)
                    if index_to_be_deleted:
                        for k in sorted(index_to_be_deleted, reverse=True):
                            del self.factorizable[j].summation[0][0].indexes[k]
                    
            #Factorize permutation operators
            commonpermutations = []
            for i in range(len(keys)):
                if self.factorizable[keys[i]].permutation:
                    supposealltrue = [True]*len(self.factorizable[keys[i]].permutation)
                    lastamplitudelables = self.factorizable[keys[i]].amplitude[-1][0].subscript + \
                        self.factorizable[keys[i]].amplitude[-1][0].superscript
                    for k in range(len(self.factorizable[keys[i]].permutation)):
                        if self.factorizable[keys[i]].permutation[k][0].subscript[0] not in lastamplitudelables \
                            and self.factorizable[keys[i]].permutation[k][0].superscript[0] not in lastamplitudelables:
                            supposealltrue[k] = False
                    for j in matched[keys[i]]:
                        for k in range(len(self.factorizable[keys[i]].permutation)):
                            if self.factorizable[keys[i]].permutation[k] not in self.factorizable[j].permutation:
                                supposealltrue[k] = False
                    tmppermutations = []
                    for k in range(len(self.factorizable[keys[i]].permutation)):
                        if supposealltrue[k]:
                            tmppermutations += self.factorizable[keys[i]].permutation[k]
                    commonpermutations.append(tmppermutations)
                else:
                    commonpermutations.append([])
                if commonpermutations[i]:
                    for item in commonpermutations[i]:
                        self.factorizable[keys[i]].permutation.remove([item])
                        for j in matched[keys[i]]:
                            self.factorizable[j].permutation.remove([item])
            for i in range(len(keys)):
                commonamplitude.append(self.factorizable[keys[i]].amplitude[-1])
            for k,v in matched.items():
                tmplist = v + [k]
                tmpoperationtree = deepcopy(OperationTree())
                for num in tmplist:
                    del self.factorizable[num].amplitude[-1]
                    tmpoperationtree.factorizable.append(deepcopy(self.factorizable[num].duplicate()))
                tmpoperationtree.children = [] #Why it works?
                self.children.append(deepcopy(tmpoperationtree.duplicate()))
            for i in range(len(keys)):
                index = keys[i]
                if len(self.factorizable[index].amplitude) == 1:
                    label = self.factorizable[index].amplitude[0][0].subscript + \
                            self.factorizable[index].amplitude[0][0].superscript
                    commonamplitude[i].insert(0,Tensor(labels = label, id =  order * 10 + i + 1))
                    if commonpermutations[i]:
                        commonamplitude[i].insert(0,commonpermutations[i])
                else:
                    label = self.factorizable[index].amplitude[0][0].subscript + \
                            self.factorizable[index].amplitude[0][0].superscript
                    for j in range(1,len(self.factorizable[index].amplitude)):
                        nextlabel = self.factorizable[index].amplitude[j][0].subscript + \
                             self.factorizable[index].amplitude[j][0].superscript
                        sharedlabel = [item for item in label if item in nextlabel]
                        label = [item for item in label if item not in sharedlabel] + \
                            [item for item in nextlabel if item not in sharedlabel]
                        commonamplitude[i].insert(0,Tensor(labels = label, id =  order * 10 + i + 1))
                        if commonpermutations[i]:
                            commonamplitude[i].insert(0,commonpermutations[i])       
            self.factorizable = deepcopy(commonamplitude)
            for i in range(len(keys)):
                self.children[i].factorizetest(iteration = iteration+1, order = order * 10 + i + 1) 
        else:
            self.factorizable = [] # unfatorizable, terms already stored in self.unfactorizable

class CodeGenerator():
    def __init__(self,OperationTree):
        self.ot = OperationTree
    