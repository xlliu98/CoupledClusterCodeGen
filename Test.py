from Classes import *
from Functions import *
from itertools import permutations
from itertools import chain
from math import factorial
from copy import deepcopy
import pickle


a_dagger = operator("p",True,0) # a^\dagger
i = operator("h",False,0) # i
b_dagger = operator("p",True,1) # b^\dagger
c_dagger = operator("p",True,2)
j = operator("h",False,1) #j
k = operator("h",False,2)
p_dagger = operator("g",True,0) #p^\dagger
q_dagger = operator("g",True, 1)#q^\dagger
r = operator("g",False,2)#r
s = operator("g",False,3)#s
i2_dagger = operator("h",True,8)
a2 = operator("p",False,8)
i3_dagger= operator("h",True,9)
a3 = operator("p",False,9)
T1 = operatorStr(summation = [[summation(deepcopy([a_dagger,i]))]], amplitude = [[amplitude([i],[a_dagger])]],operator = [[a_dagger,i]])
T2 = operatorStr(coefficient = Fraction(1,4), summation = [[summation([a_dagger,b_dagger,i,j])]], amplitude = [[amplitude([i,j],[a_dagger,b_dagger])]],operator = [[a_dagger,b_dagger,j,i]])
T1_t = operatorStr(operator = [[a_dagger,i]])
T2_t = operatorStr(coefficient = Fraction(1,4), operator = [[b_dagger,c_dagger,k,j]])
V_t = operatorStr(coefficient = Fraction(1,4), operator = [[p_dagger,q_dagger,s,r]])
F_t = operatorStr(operator = [[p_dagger,r]])
F = operatorStr(summation = [[summation(deepcopy([p_dagger,r]))]], amplitude = [[amplitude([p_dagger],[r],2)]],operator = [[p_dagger,r]])
V = operatorStr(coefficient = Fraction(1,4), summation = [[summation([p_dagger,q_dagger,r,s])]], amplitude = [[amplitude([p_dagger,q_dagger],[r,s],1)]],operator = [[p_dagger,q_dagger,s,r]])

H = F + V
D = T1 + T2


test = hausdoffExpansionConnected(H,D)

test.canonicalize()
test.combine()

for item in test.operatorStringList:
    #item.operator.insert(0,[i2_dagger,a2])
    item.operator.insert(0,[i2_dagger, i3_dagger, a3, a2])
test.deleteVanishingTerm()



test.makeDistinctLabel()

result = test.contract()

result.deleteDisconnectedDiagram()
result.relabel()


result.combine()

result.combineCyclicTerms()

result.findPermutationandCombine()
result.findPermutationandCombine()

result.combinebyFullPermutationofCommonIndexes()

result.replaceAllbyBestContractionOrder()
result.extractAllPermutation()
for opstr in result.operatorStringList:
    for perm in opstr.permutation:
        perm[0].canonicalize()
for opstr in result.operatorStringList:
    opstr.permutation.sort()
print(result)
print(len(result))
with open('ccsd_doubles_aug10.pkl','wb') as output:
    pickle.dump(result,output,pickle.HIGHEST_PROTOCOL)



#parity = list(itertools.chain(*testOpStr1.operator)).index(i)
#testOpStr1.coefficient *= (-1)**parity
#
#firstInSum = p_dagger in list(itertools.chain(*[item[0].indexes for item in testOpStr1.summation]))
#if firstInSum:
#    for item in testOpStr1.summation:
#        if p_dagger in item[0].indexes:
#            indexes_tmp = deepcopy(item[0].indexes)
#            del indexes_tmp[indexes_tmp.index(p_dagger)] 
#            item[0].indexes = deepcopy(indexes_tmp)
#            print(testOpStr1)
#            break
#    for item in testOpStr1.amplitude:
#        if item[0].hasOperator(p_dagger):
#            item[0].replace(p_dagger,i)
#            print(testOpStr1)
#            break
#
#del testOpStr1.operator[0][0]
#
#for item in testOpStr1.operator:
#    if i in item:
#        del item[item.index(i)]    
#        break

        