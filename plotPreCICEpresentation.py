import numpy as np 
from pathlib import Path
import os
from matplotlib import pyplot as plt
import re
import pandas as pd
import json

import Problem_FSI
import heatCoupling
from FSI_verification import get_problem, get_solver, solve_monolithic
from FSI_verification import get_parameters, get_init_cond


plt.rcParams['lines.linewidth'] = 2
plt.rcParams['font.size'] = 18
plt.rcParams['lines.markersize'] = 12


def plot_case(path, which):

    p = Path(path)
    dirs = [x for x in p.iterdir() if (x.is_dir() and str(x) != 'templates'and str(x) != 'templates_precice')]
    Tols = []
    UD = []
    UN = []
    Ug = []
    itersQN = []
    itersR = []
    totalTimeStepsQN = []

    UDP = []
    UNP = []
    UgP = []
    totalTimeStepsP = []
    totalitersP = []

    UDRO = []
    UNRO = []
    UgRO = []
    totalTimeStepsRO = []
    totalitersRO = []


    for dir in dirs:
        st_dir = str(dir)
        st_dir_ls = st_dir.split('/')
    
        Tols.append(float(st_dir_ls[-1]))
        print(st_dir)
        with open(st_dir+"/QuasiNewton/resultsQN_dirFalse", 'r') as myfile:
            resultsNQN = json.load(myfile)

        with open(st_dir+"/QuasiNewton/resultsQN_dirTrue", 'r') as myfile:
            resultsDQN = json.load(myfile)

        with open(st_dir+"/PRelaxation/resultsQN_dirFalse", 'r') as myfile:
            resultsRelaxPN = json.load(myfile)

        with open(st_dir+"/PRelaxation/resultsQN_dirTrue", 'r') as myfile:
            resultsRelaxPD = json.load(myfile)
        
        with open(st_dir+"/QuasiNewton/resultsRelaxation", 'r') as myfile:
            resultsRO = json.load(myfile)

        

        UD.append(resultsDQN['uDomain'])
        UN.append(resultsNQN['uDomain'])
        Ug.append(resultsNQN['ug'])
        itersQN.append(resultsDQN['iters'])
        totalTimeStepsQN.append(resultsDQN['totalTimeSteps'] + resultsNQN['totalTimeSteps'])

        UDP.append(resultsRelaxPD['uDomain'])
        UNP.append(resultsRelaxPN['uDomain'])
        UgP.append(resultsRelaxPN['ug'])
        totalitersP.append(resultsRelaxPD['iters'])
        totalTimeStepsP.append(resultsRelaxPD['totalTimeSteps'] + resultsRelaxPN['totalTimeSteps'])
    
        UDRO.append(resultsRO['u1'])
        UNRO.append(resultsRO['u2'])
        UgRO.append(resultsRO['ug0'])
        totalitersRO.append(resultsRO['iters'])
        totalTimeStepsRO.append(resultsRO['totalTimeSteps'])

    
    
    print(Tols)

    UD = [x for _,x in sorted(zip(Tols,UD), key = lambda pair: pair[0], reverse=True)]
    UN = [x for _,x in sorted(zip(Tols,UN), key = lambda pair: pair[0], reverse=True)]
    Ug = [x for _,x in sorted(zip(Tols,Ug), key = lambda pair: pair[0], reverse=True)]
    itersQN = [x for _,x in sorted(zip(Tols,itersQN), key = lambda pair: pair[0], reverse=True)]
    totalTimeStepsQN = [x for _,x in sorted(zip(Tols,totalTimeStepsQN), key = lambda pair: pair[0], reverse=True)]
    
    UDP = [x for _,x in sorted(zip(Tols,UDP), key = lambda pair: pair[0], reverse=True)]
    UNP = [x for _,x in sorted(zip(Tols,UNP), key = lambda pair: pair[0], reverse=True)]
    UgP = [x for _,x in sorted(zip(Tols,UgP), key = lambda pair: pair[0], reverse=True)]
    totalitersP = [x for _,x in sorted(zip(Tols,totalitersP), key = lambda pair: pair[0], reverse=True)]
    totalTimeStepsP = [x for _,x in sorted(zip(Tols,totalTimeStepsP), key = lambda pair: pair[0], reverse=True)]

    UDRO = [x for _,x in sorted(zip(Tols,UDRO), key = lambda pair: pair[0], reverse=True)]
    UNRO = [x for _,x in sorted(zip(Tols,UNRO), key = lambda pair: pair[0], reverse=True)]
    UgRO = [x for _,x in sorted(zip(Tols,UgRO), key = lambda pair: pair[0], reverse=True)]
    totalitersRO = [x for _,x in sorted(zip(Tols,totalitersRO), key = lambda pair: pair[0], reverse=True)]
    totalTimeStepsRO = [x for _,x in sorted(zip(Tols,totalTimeStepsRO), key = lambda pair: pair[0], reverse=True)]


    Tols = sorted(Tols,reverse=True)

    pp = get_parameters(which)
    p2 = {'n': 100, 'dim': 2,'WR_type': 'DNWR', **pp}
    prob = get_problem(**p2)

    uWhole = [[np.array(u1),np.array(u2),np.array(ug)] for u1,ug,u2 in zip(UD,Ug,UN)]
    errorQN = [prob.norm_inner(uWhole[i][0]-uWhole[-1][0],uWhole[i][1]-uWhole[-1][1],uWhole[i][2]-uWhole[-1][2]) for i in range(0,len(uWhole)-1)]
    
    uWhole = [[np.array(u1),np.array(u2),np.array(ug)] for u1,ug,u2 in zip(UDP,UgP,UNP)]
    errorP = [prob.norm_inner(uWhole[i][0]-uWhole[-1][0],uWhole[i][1]-uWhole[-1][1],uWhole[i][2]-uWhole[-1][2]) for i in range(0,len(uWhole)-1)]    
    
    uWhole = [[np.array(u1),np.array(u2),np.array(ug)] for u1,ug,u2 in zip(UDRO,UgRO,UNRO)]
    errorRO = [prob.norm_inner(uWhole[i][0]-uWhole[-1][0],uWhole[i][1]-uWhole[-1][1],uWhole[i][2]-uWhole[-1][2]) for i in range(0,len(uWhole)-1)]

    return totalTimeStepsP, totalTimeStepsQN,totalTimeStepsRO, errorQN, errorP, errorRO, Tols, itersQN, totalitersP, totalitersRO

def plot_caseConstant(path, which):

    p = Path(path)
    dirs = [x for x in p.iterdir() if (x.is_dir() and str(x) != 'templates'and str(x) != 'templates_precice')]
    Tols = []
    UD = []
    UN = []
    Ug = []
    itersQN = []
    itersR = []
    totalTimeStepsQN = []

    UDP = []
    UNP = []
    UgP = []
    totalTimeStepsP = []
    totalitersP = []

    for dir in dirs:
        st_dir = str(dir)
        st_dir_ls = st_dir.split('/')
    
        Tols.append(float(st_dir_ls[-1]))
        print(st_dir)
        with open(st_dir+"/QuasiNewton/resultsQN_dirFalse", 'r') as myfile:
            resultsNQN = json.load(myfile)

        with open(st_dir+"/QuasiNewton/resultsQN_dirTrue", 'r') as myfile:
            resultsDQN = json.load(myfile)

        # with open(st_dir+"/PRelaxation/resultsQN_dirFalse", 'r') as myfile:
        #     resultsRelaxPN = json.load(myfile)

        # with open(st_dir+"/PRelaxation/resultsQN_dirTrue", 'r') as myfile:
        #     resultsRelaxPD = json.load(myfile)

        UD.append(resultsDQN['uDomain'])
        UN.append(resultsNQN['uDomain'])
        Ug.append(resultsNQN['ug'])
        itersQN.append(resultsDQN['iters'])
        totalTimeStepsQN.append(resultsDQN['totalTimeSteps'] + resultsNQN['totalTimeSteps'])

        # UDP.append(resultsRelaxPD['uDomain'])
        # UNP.append(resultsRelaxPN['uDomain'])
        # UgP.append(resultsRelaxPN['ug'])
        # totalitersP.append(resultsRelaxPD['iters'])
        # totalTimeStepsP.append(resultsRelaxPD['totalTimeSteps'] + resultsRelaxPN['totalTimeSteps'])

    UD = [x for _,x in sorted(zip(Tols,UD), key = lambda pair: pair[0])]
    UN = [x for _,x in sorted(zip(Tols,UN), key = lambda pair: pair[0])]
    Ug = [x for _,x in sorted(zip(Tols,Ug), key = lambda pair: pair[0])]
    itersQN = [x for _,x in sorted(zip(Tols,itersQN), key = lambda pair: pair[0])]
    totalTimeStepsQN = [x for _,x in sorted(zip(Tols,totalTimeStepsQN), key = lambda pair: pair[0])]
    
    # UDP = [x for _,x in sorted(zip(Tols,UDP), key = lambda pair: pair[0])]
    # UNP = [x for _,x in sorted(zip(Tols,UNP), key = lambda pair: pair[0])]
    # UgP = [x for _,x in sorted(zip(Tols,UgP), key = lambda pair: pair[0])]
    # totalitersP = [x for _,x in sorted(zip(Tols,totalitersP), key = lambda pair: pair[0])]
    # totalTimeStepsP = [x for _,x in sorted(zip(Tols,totalTimeStepsP), key = lambda pair: pair[0])]

    Tols = sorted(Tols)

    pp = get_parameters(which)
    p2 = {'n': 100, 'dim': 2,'WR_type': 'DNWR', **pp}
    prob = get_problem(**p2)

    uWhole = [[np.array(u1),np.array(u2),np.array(ug)] for u1,ug,u2 in zip(UD,Ug,UN)]
    errorQN = [prob.norm_inner(uWhole[i][0]-uWhole[-1][0],uWhole[i][1]-uWhole[-1][1],uWhole[i][2]-uWhole[-1][2]) for i in range(0,len(uWhole)-1)]

    # uWholeP = [np.concatenate([np.array(u1),np.array(ug),np.array(u2)]) for u1,ug,u2 in zip(UDP,UgP,UNP)]
    # errorP = [np.linalg.norm(uWholeP[i] - uWholeP[-1]) for i in range(0,len(uWholeP)-1)]    
    
    return totalTimeStepsQN, errorQN, Tols, itersQN

p = Path('experiments/')
dirs = [x for x in p.iterdir() if (x.is_dir() and str(x) != 'templates'and str(x) != 'templates_precice')   ]
print(dirs)
for dir in dirs:
   
   
    st_dir = str(dir)
    st_dir_ls = st_dir.split('/')
    totalTimeStepsP, totalTimeStepsQN,totalTimeStepsRO, errorQN, errorP, errorRO, Tols, itersQN, totalitersP, totalitersRO = plot_case(st_dir+'/adaptive/', st_dir_ls[-1])
    totalTimeStepsQNF, errorQNF, TolsF, itersQNF = plot_caseConstant(st_dir+'/fixed/', st_dir_ls[-1])
    which = st_dir_ls[-1]
    
    plt.figure()
    plt.loglog(totalTimeStepsQN[:-1],errorQN, label='QN TA', linestyle='--', marker='*')
    plt.loglog(totalTimeStepsP[:-1],errorP, label='rel TA PreCICE', linestyle='--', marker='.')
    plt.loglog(totalTimeStepsRO[:-1],errorRO, label='rel TA python', linestyle='--', marker='x')
    plt.loglog(totalTimeStepsQNF[:-1],errorQNF, label='QN Mult', linestyle='--', marker='v')

    plt.xlabel('Total number of time steps')
    plt.ylabel('Error')
    plt.legend()
    plt.grid(True, 'major')
    plt.savefig(which + 'efficiency.png', bbox_inches="tight", dpi=300)

    plt.figure()
    plt.semilogx(Tols,itersQN, label='Quasi-Newton', linestyle='--', marker='*')
    plt.semilogx(Tols,totalitersP, label='relax PreCICe', linestyle='--', marker='.')


    plt.xlabel('tolerance')
    plt.ylabel('Iterations')
    plt.legend()
    plt.grid(True, 'major')
    plt.savefig(which + 'iterVsTol.png',bbox_inches="tight", dpi=300)





