from jinja2 import Environment, select_autoescape, FileSystemLoader
import argparse
import os, stat

from numpy import double
import shutil

parser = argparse.ArgumentParser()
parser.add_argument("-testCases", "--testCases", default=["water_steel","air_water","air_steel"], type=list)
# parser.add_argument("-testCases", "--testCases", default=["air_water","air_steel"], type=list)
parser.add_argument("-nbrTols","--nbrTols", default = 6,type = int)

args = parser.parse_args()
path_templates = './templates'

env = Environment(
    loader=FileSystemLoader(path_templates),
    autoescape=select_autoescape(['xml', 'json'])
)


precice_config_template = env.get_template('precice-config.xml')
paths = []

for which in args.testCases: 
    for i in range(0,args.nbrTols):
        tol = 10**(-1-i)

        target_path = os.path.join("experiments", str(which),str(tol), str("QuasiNewton"))
        paths.append(target_path)
        if not os.path.exists(target_path):
            os.makedirs(target_path)


        relaxBash = "run_relaxation.sh"
        dir = env.get_template(relaxBash)
        
        with open(os.path.join( target_path, relaxBash), "w") as file:
            file.write(dir.render(tol=tol, case=which))


        precice_config_name = "precice-config.xml"

        with open(os.path.join( target_path, precice_config_name), "w") as file:
            file.write(precice_config_template.render(tol=tol))
        
        dirichletPath = os.path.join(target_path, "Dirichlet")
        if not os.path.exists(dirichletPath):
            os.makedirs(dirichletPath)
        
        stuff = which.split('_')

        dirichletSolver = "Dirichlet/run.sh"
        dir = env.get_template(dirichletSolver)
        
        with open(os.path.join( dirichletPath, "run.sh"), "w") as file:
            file.write(dir.render(tol=tol, case=stuff[0]))

        neumannPath = os.path.join(target_path, "Neumann")
        if not os.path.exists(neumannPath):
            os.makedirs(neumannPath)


        neumannSolver = "Neumann/run.sh"
        neu = env.get_template(neumannSolver)
        with open(os.path.join( neumannPath, "run.sh"), "w") as file:
            file.write(neu.render(tol=tol, case=stuff[1]))

        destHeat = os.path.join( target_path, "heatCoupling.py")
        shutil.copyfile("templates/heatCoupling.py",destHeat)

        dest = os.path.join( target_path, "dt_control.py")
        shutil.copyfile("templates/dt_control.py",dest)

        dest = os.path.join( target_path, "FSI_verification.py")
        shutil.copyfile("templates/FSI_verification.py",dest)

        dest = os.path.join( target_path, "FSI_verification.py")
        shutil.copyfile("templates/FSI_verification.py",dest)

        dest = os.path.join( target_path, "Problem_FSI_1D.py")
        shutil.copyfile("templates/Problem_FSI_1D.py",dest)

        dest = os.path.join( target_path, "Problem_FSI_2D.py")
        shutil.copyfile("templates/Problem_FSI_2D.py",dest)

        dest = os.path.join( target_path, "Problem_FSI.py")
        shutil.copyfile("templates/Problem_FSI.py",dest)

        dest = os.path.join( target_path, "relaxation.py")
        shutil.copyfile("templates/relaxation.py",dest)

    # run_path = os.path.join( "experiments", 'runall.sh')
    # run_template = env.get_template("run_time_order_template.sh")
    # with open(run_path, "w") as file:
    #     file.write(run_template.render(paths = paths))

precice_config_template = env.get_template('precice-config_relax.xml')

import Problem_FSI
import heatCoupling
from FSI_verification import get_problem, get_solver, solve_monolithic
from FSI_verification import get_parameters, get_init_cond

def get_relax_param(which, TOL_D):
    pp = get_parameters(which)
    p2 = {'n': 100, 'dim': 2,'WR_type': 'DNWR', **pp}
    prob = get_problem(**p2)

    u10, u20, ug0 = prob.get_initial_values(
            get_init_cond(2, num=1))
    dtD = prob.get_dt0(1e4, TOL_D, u10, which=1)
    dtN = prob.get_dt0(1e4, TOL_D, u20, which=2)
    dt = max(dtD,dtN)
    print("Correct theta" + str(prob.DNWR_theta_opt(dt,dt)))
    print("My wrong theta" + str(prob.DNWR_theta_opt(dtD*100,100*dtN)))

    return prob.DNWR_theta_opt(dt,dt)
    
for which in args.testCases: 
    for i in range(0,args.nbrTols):
        tol = 10**(-1-i)

        target_path = os.path.join("experiments", str(which),str(tol), str("PRelaxation"))
        paths.append(target_path)
        if not os.path.exists(target_path):
            os.makedirs(target_path)

        precice_config_name = "precice-config.xml"

        with open(os.path.join( target_path, precice_config_name), "w") as file:
            file.write(precice_config_template.render(tol=tol, relax=get_relax_param(which,tol)))
        
        dirichletPath = os.path.join(target_path, "Dirichlet")
        if not os.path.exists(dirichletPath):
            os.makedirs(dirichletPath)
        
        stuff = which.split('_')

        dirichletSolver = "Dirichlet/run.sh"
        dir = env.get_template(dirichletSolver)
        
        with open(os.path.join( dirichletPath, "run.sh"), "w") as file:
            file.write(dir.render(tol=tol, case=stuff[0]))

        neumannPath = os.path.join(target_path, "Neumann")
        if not os.path.exists(neumannPath):
            os.makedirs(neumannPath)


        neumannSolver = "Neumann/run.sh"
        neu = env.get_template(neumannSolver)
        with open(os.path.join( neumannPath, "run.sh"), "w") as file:
            file.write(neu.render(tol=tol, case=stuff[1]))

        destHeat = os.path.join( target_path, "heatCoupling.py")
        shutil.copyfile("templates/heatCoupling.py",destHeat)

        dest = os.path.join( target_path, "dt_control.py")
        shutil.copyfile("templates/dt_control.py",dest)

        dest = os.path.join( target_path, "FSI_verification.py")
        shutil.copyfile("templates/FSI_verification.py",dest)

        dest = os.path.join( target_path, "FSI_verification.py")
        shutil.copyfile("templates/FSI_verification.py",dest)

        dest = os.path.join( target_path, "Problem_FSI_1D.py")
        shutil.copyfile("templates/Problem_FSI_1D.py",dest)

        dest = os.path.join( target_path, "Problem_FSI_2D.py")
        shutil.copyfile("templates/Problem_FSI_2D.py",dest)

        dest = os.path.join( target_path, "Problem_FSI.py")
        shutil.copyfile("templates/Problem_FSI.py",dest)

        dest = os.path.join( target_path, "relaxation.py")
        shutil.copyfile("templates/relaxation.py",dest)

        dest = os.path.join( target_path, "run_relaxation.sh")
        shutil.copyfile("templates/run_relaxationPreRelax.sh",dest)


    run_path = os.path.join( "experiments", 'runall.sh')
    run_template = env.get_template("run_time_order_template.sh")
    with open(run_path, "w") as file:
        file.write(run_template.render(paths = paths))

    # shutil.copytree(path_templates+"/tools",os.path.join("experiments","tools"))
    # with open(run_path, "w") as file:
    #     file.write(run_template.render(paths = paths))




