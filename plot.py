import numpy as np 
from pathlib import Path
import os
from matplotlib import pyplot as plt
import re
import pandas as pd
import json

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

    UDR = []
    UNR = []
    UgR = []
    totalTimeStepsR = []

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

        with open(st_dir+"/PRelaxation/resultsQN_dirFalse", 'r') as myfile:
            resultsRelaxPN = json.load(myfile)

        with open(st_dir+"/PRelaxation/resultsQN_dirTrue", 'r') as myfile:
            resultsRelaxPD = json.load(myfile)

        with open(st_dir+"/QuasiNewton/resultsRelaxation", 'r') as myfile:
            resultsR = json.load(myfile)

        UD.append(resultsDQN['uDomain'])
        UN.append(resultsNQN['uDomain'])
        Ug.append(resultsNQN['ug'])
        itersQN.append(resultsDQN['iters'])
        totalTimeStepsQN.append(resultsDQN['totalTimeSteps'] + resultsNQN['totalTimeSteps'])

        UDR.append(resultsR['u1'])
        UNR.append(resultsR['u2'])
        UgR.append(resultsR['ug0'])
        totalTimeStepsR.append(resultsR['totalTimeSteps'])
        itersR.append(resultsR['iters'])

        UDP.append(resultsRelaxPD['uDomain'])
        UNP.append(resultsRelaxPN['uDomain'])
        UgP.append(resultsRelaxPN['ug'])
        totalitersP.append(resultsRelaxPD['iters'])
        totalTimeStepsP.append(resultsRelaxPD['totalTimeSteps'] + resultsRelaxPN['totalTimeSteps'])
    print(Tols)

    UD = [x for _,x in sorted(zip(Tols,UD), key = lambda pair: pair[0], reverse=True)]
    UN = [x for _,x in sorted(zip(Tols,UN), key = lambda pair: pair[0], reverse=True)]
    Ug = [x for _,x in sorted(zip(Tols,Ug), key = lambda pair: pair[0], reverse=True)]
    itersQN = [x for _,x in sorted(zip(Tols,itersQN), key = lambda pair: pair[0], reverse=True)]
    totalTimeStepsQN = [x for _,x in sorted(zip(Tols,totalTimeStepsQN), key = lambda pair: pair[0], reverse=True)]

    UDR = [x for _,x in sorted(zip(Tols,UDR), key = lambda pair: pair[0], reverse=True)]
    UNR = [x for _,x in sorted(zip(Tols,UNR), key = lambda pair: pair[0], reverse=True)]
    UgR = [x for _,x in sorted(zip(Tols,UgR), key = lambda pair: pair[0], reverse=True)]
    itersR = [x for _,x in sorted(zip(Tols,itersR), key = lambda pair: pair[0], reverse=True)]
    totalTimeStepsR = [x for _,x in sorted(zip(Tols,totalTimeStepsR), key = lambda pair: pair[0], reverse=True)]
    
    UDP = [x for _,x in sorted(zip(Tols,UDP), key = lambda pair: pair[0], reverse=True)]
    UNP = [x for _,x in sorted(zip(Tols,UNP), key = lambda pair: pair[0], reverse=True)]
    UgP = [x for _,x in sorted(zip(Tols,UgP), key = lambda pair: pair[0], reverse=True)]
    totalitersP = [x for _,x in sorted(zip(Tols,totalitersP), key = lambda pair: pair[0], reverse=True)]
    totalTimeStepsP = [x for _,x in sorted(zip(Tols,totalTimeStepsP), key = lambda pair: pair[0], reverse=True)]

    Tols = sorted(Tols,reverse=True)

    uWhole = [np.concatenate([np.array(u1),np.array(ug),np.array(u2)]) for u1,ug,u2 in zip(UD,Ug,UN)]
    errorQN = [np.linalg.norm(uWhole[i] - uWhole[-1]) for i in range(0,len(uWhole)-1)]

    uWholeR = [np.concatenate([np.array(u1),np.array(ug),np.array(u2)]) for u1,ug,u2 in zip(UDR,UgR,UNR)]
    errorR = [np.linalg.norm(uWholeR[i] - uWholeR[-1]) for i in range(0,len(uWholeR)-1)]    

    uWholeP = [np.concatenate([np.array(u1),np.array(ug),np.array(u2)]) for u1,ug,u2 in zip(UDP,UgP,UNP)]
    errorP = [np.linalg.norm(uWholeP[i] - uWholeP[-1]) for i in range(0,len(uWholeP)-1)]    

    
    plt.figure()
    plt.loglog(totalTimeStepsQN[:-1],errorQN, label='Quasi-Newton', linestyle='--', marker='*')
    plt.loglog(totalTimeStepsR[:-1],errorR, label='optimal relax', linestyle='--', marker='+')
    plt.loglog(totalTimeStepsP[:-1],errorP, label='relax PreCICe', linestyle='--', marker='.')

    # labelpad=-20, position=(1.05, -1), fontsize=20
    plt.xlabel('Number of time steps')
    # rotation=0, labelpad=-50, position=(2., 1.0), fontsize=20
    plt.ylabel('Error')
    plt.legend()
    plt.grid(True, 'major')
    plt.savefig(which + 'efficiency.png', bbox_inches="tight", dpi=300)

    plt.figure()
    plt.semilogx(Tols,itersQN, label='Quasi-Newton', linestyle='--', marker='*')
    plt.semilogx(Tols,itersR, label='optimal relax', linestyle='--', marker='+')
    plt.semilogx(Tols,totalitersP, label='relax PreCICe', linestyle='--', marker='.')

    # labelpad=-20, position=(1.05, -1), fontsize=20
    plt.xlabel('tolerance')
    # rotation=0, labelpad=-50, position=(2., 1.0), fontsize=20
    plt.ylabel('Iterations')
    plt.legend()
    plt.grid(True, 'major')
    plt.savefig(which + 'iterVsTol.png',bbox_inches="tight", dpi=300)


    
    return
p = Path('experiments/')
dirs = [x for x in p.iterdir() if (x.is_dir() and str(x) != 'templates'and str(x) != 'templates_precice')]
for dir in dirs:
   
   
    st_dir = str(dir)
    st_dir_ls = st_dir.split('/')
    plot_case(st_dir+'/', st_dir_ls[-1])



