from __future__ import division
import csv
import xlrd


# select next move
def selection(gamma, b, c):
    payoff = [gamma[x] * (b[x] / c[x]) for x in range(0, len(gamma))]
    temp = [round(i,2) for i in payoff]
    selected = payoff.index(max(payoff))
    while C_M + c[selected] > G:
        gamma[selected] = 0
        if sum(gamma) == 0:
            print "Out of options or budget"
            selected = -1
            break
        payoff = [gamma[x] * (b[x] / c[x]) for x in range(0, len(gamma))]
        selected = payoff.index(max(payoff))

    return selected


# update vector gamma after a successful action
def gamma_update(gamma, conf, trust, cat, selected, T, o):
    for i in range(0, len(gamma)):
        if i in o:
            gamma[i] = 0
            # print "i in o"
        elif any(trust[x][cat[i][0]] < conf[i] for x in cat[selected]):
            gamma[i] = T[selected][i]
            conf[i] = min(trust[x][cat[i][0]] for x in cat[selected])
        elif any(trust[x][cat[i][0]] == conf[i] for x in cat[selected]):
            gamma[i] = max(T[selected][i], gamma[i])
        else:
            pass
    return gamma, conf

# update trust vector after a successful action
def update_categories_found(categories, selected, cat):
    for i in cat[selected]:
        if i not in categories:
            categories.append(i)
    return categories


def debug(o, selected, gamma, categories):
    print '\nSelected action', selected
    print "attack vector A: ", A
    print 'ordering', o
    s = "vector gamma "
    for i in range(0, len(gamma)):
        s += str(i) + ":" + str(gamma[i]) + ", "
    print s
    print gamma
    print 'categories', categories


# main

T = []
with open('/home/zen/Desktop/ttp_relationships.csv') as csvDataFile:
    csvReader = csv.reader(csvDataFile)
    for row in csvReader:
        T.append(row)

# make T float
for i in range(0, len(T)):
    for j in range(0, len(T)):
        T[i][j] = float(T[i][j])

categories = []
cat = {}
conf = []

# read categories for each TTP
with open('/home/zen/Desktop/categories.csv') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        cat[int(row[0])] = row[1:]

for x in cat:
    cat[x] = [i for i in cat[x] if i != '']

book = xlrd.open_workbook('/home/zen/Desktop/cost_benefit.xlsx')
sheet = book.sheet_by_name('Sheet1')
b = [sheet.cell_value(r, 3) for r in range(sheet.nrows)] # read benefit values
c = [sheet.cell_value(r, 4) for r in range(sheet.nrows)] # read cost values

b = b[1:]
b = [i for i in b if i != '']
c = c[1:]
c = [i for i in c if i != '']

# read trust values per category pair
d={}
with open('/home/zen/Desktop/trust.csv') as csvDataFile:
    data=csv.reader(csvDataFile, delimiter=',')
    headers=next(data)[1:]
    for row in data:
        d[row[0]]={key: int(value) for key, value in zip(headers,row[1:])}

#one incident should be uncomment
#A=[13, 12, 10, 17, 8, 2, 15, 6] #incident 1
A=[14, 11, 12,17, 10, 23, 15, 0, 24] # incident 2
# A= [15,12, 29, 30,0,10] #incident 3

# Constants
G = 65 # budget (this changes per incident)
C_M = 0  # time (cost) spend until step M

# Initialisation using given trigger action
trigger_action = input("Select from A:"+str(A))
trigger = A.index(trigger_action)  # trigger action
categories = [x for x in cat[A[trigger]]]
o = [A[trigger]]  # ordering vector creation and initialization
gamma = T[A[trigger]]  # available actions on current step
print gamma
conf = [d[cat[trigger_action][0]][cat[i][0]] for i in range(0, len(gamma))] # trust vector at current state
revealed = [A[trigger]]  # malicious actions revealed so far
B_M = b[trigger_action]  # collected benefit until step M

while (sum(gamma) != 0) & (not set(A).issubset(o)): # continue until there are available action to investigate or incident is fully uncovered
    #raw_input("Press Enter to continue...") # enable for debug at each step
    next_action = selection(gamma, b, c, conf)
    #debug(o, next_action, gamma, categories, conf, C_M, revealed) #enable for debug at each step
    if next_action == -1:
        break
    o.append(next_action) # append selected action to ordering
    C_M = C_M + c[next_action] # add cost of selected action
    if next_action in A: # if action uncovers evidence collect benefit and update revealed vector
        revealed.append(next_action)
        B_M = B_M + b[next_action]
        gamma, conf = gamma_update(gamma, conf, d, cat, next_action, T, o)
        categories = update_categories_found(categories, next_action, cat)
    else:
        gamma[next_action] = 0


temp = [i for i in A if i not in revealed] # calculate missed action
print "Ordering:", o
print "Attack actions revealed:", revealed
print "Attack action missed:", temp
print "Ratio: ", len(o) / len(A)
print "extra: ", [i for i in o if i not in A]
print "Benefit collected:", B_M
print "Remaining budget:", G - C_M
