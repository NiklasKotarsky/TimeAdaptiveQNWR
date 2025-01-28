#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 16:20:34 2020

@author: Peter Meisrimel, Lund University
"""

import numpy as np
import precice
import json


def solve_dirichlet_SDIRK2(self, dt, uold,ug_old, read_data):
    dta = self.a*dt
    ug_old, ug_new, ug_mid = read_data[0], read_data[2], read_data[1]
    ug_dot_a = (ug_mid - ug_old)/dta
    ug_dot_new = (ug_new - (ug_old + (1 - self.a)*dt*ug_dot_a))/dta

    # stage 1
    s1 = uold
    U1 = self.linear_solver(self.M1 + dta*self.A1,
                            self.M1.dot(s1) - dta*(self.M1g.dot(ug_dot_a) + self.A1g.dot(ug_mid)))
    k1 = (U1 - s1)/dta

    # stage 2
    s2 = uold + dt*(1 - self.a)*k1
    U2 = self.linear_solver(self.M1 + dta*self.A1,
                            self.M1.dot(s2) - dta*(self.M1g.dot(ug_dot_new) + self.A1g.dot(ug_new)))
    k2 = (U2 - s2)/dta

    localu = dt*((self.a - self.ahat)*k2 + (self.ahat - self.a)*k1)

    flux_2 = self.Mgg1.dot(ug_dot_new) + self.Mg1.dot(k2) + \
        self.Agg1.dot(ug_new) + self.Ag1.dot(U2)
    #u1, ug, write_data, le
    return U2, ug_new, flux_2, localu

def solve_neumann_SDIRK2(self, dt, uold, ug_old, read_data):
    dta = self.a*dt
    n = len(ug_old)
    flux1 = read_data[1]
    flux2 = read_data[2]
    uold_full = np.hstack((uold, ug_old))

    s1 = uold_full  # stage 1
    b = self.Neumann_M.dot(s1)
    b[-n:] -= dta*flux1
    U1 = self.linear_solver(self.Neumann_M + dta*self.Neumann_A, b)
    k1 = (U1 - s1)/dta

    s2 = s1 + dt*(1 - self.a)*k1  # stage 2
    b = self.Neumann_M.dot(s2)
    b[-n:] -= dta*flux2
    U2 = self.linear_solver(self.Neumann_M + dta*self.Neumann_A, b)
    k2 = (U2 - s2)/dta

    localu = dt*((self.a - self.ahat)*k2 + (self.ahat - self.a)*k1)
    
    return U2[:-n], U2[-n:], U2[-n:], localu

def runRelaxation(self,init_cond, TOL, tf, maxiter=1000, **kwargs):    
    print("peters")

    if self.WR_type != 'DNWR':
        raise ValueError('invalid solution method')
    print('TOL = ', TOL)
    TOL_FP, TOL_D, TOL_N = TOL, TOL/5, TOL/5  # paper
    u10, u20, ug0 = self.get_initial_values(init_cond)  # different for 1D and 2D

    flux0 = np.zeros(ug0.shape)  # placeholder only

    # intitial timesteps do not change
    dt0_D = self.get_dt0(1, TOL_D, u10, which=1)
    dt0_N = self.get_dt0(1, TOL_N, u20, which=2)

    t1, t2_old = [0., tf], [0., tf]  # initial time grids
    ug_WF_old = [np.copy(ug0), np.copy(ug0)]  # waveform of ug, N grid
    ug_WF_new = [np.copy(ug0), np.copy(ug0)]  # waveform of ug, N grid

    W, V = [], []
    timesteps = 0  # counter for total number of timesteps

    updates = []
    flux0 = -self.lambda_diff*ug0-self.der@u10

    
    rel_tol_fac = self.norm_interface(ug0)

    for k in range(maxiter):
        # Dirichlet time-integration
        t, u1 = 0., np.copy(u10)  # init time-integration
        dt = dt0_D  # initial timesteps
        t1, t1_stage = [0.], [0.]  # time grids
        # data for flux WF, placeholders
        flux_WF_1, flux_WF_2 = [np.copy(flux0)], [np.copy(flux0)]

        self.r_old = TOL_D  # for PI controller
        ug_WF_func = self.interpolation(
            t2_old, ug_WF_old)  # interface values WF

        u1_list = []  # storage for initial flux computation
        # adaptive time-integration loop, iterate while current timestep does not overstep tf
        while t + dt < tf-1e-10:
            
            f = []
            read_times = [0, self.a*dt, dt]
            for i in range(len(read_times)):
                read_data =  ug_WF_func(t+read_times[i])
                f.append(read_data)
            
            #U2, ug_new, flux_2, localu
            u1, _, flux2,err1 = self.solve_dirichlet_SDIRK2(dt, u1,read_data[0], f)
            
            t += dt
            t1.append(t)
            flux_WF_2.append(flux2)  # value on full timestep
            # storage for initial flux computation, saves up to 2 values, and their timesteps
            if len(u1_list) < 2:
                u1_list.append((dt, np.copy(u1)))
            dt = self.get_new_dt_PI(dt, self.norm_inner(
                err1, 'D'), TOL_D)  # PI controller
            if dt < 1e-14:
                # prevents too small timesteps
                raise ValueError('too small timesteps, aborting')
            
        # final timestep, truncate to hit tf
        dt = tf - t

        f = []
        read_times = [0, self.a*dt, dt]
        for i in range(len(read_times)):
            read_data =  ug_WF_func(t+read_times[i])
            f.append(read_data)


        u1, _, flux2, _ = self.solve_dirichlet_SDIRK2(dt, u1,read_data[0], f)
        t1.append(tf)
        flux_WF_2.append(flux2)
        if len(u1_list) < 2:  # storage for initial flux computation
            u1_list.append((dt, np.copy(u1)))

        # Neumann time-integration
        t, u2, ug_old = 0., np.copy(u20), np.copy(ug0)
        dt = dt0_N

        # inserting initial flux here
        flux_WF_1[0], flux_WF_2[0] = flux0, flux0
        flux_WF_2_func = self.interpolation(t1, flux_WF_2)

        self.r_old = TOL_D  # for PI controller
        t2_new, ug_WF_new = [0.], [np.copy(ug0)]
        ug_new = ug0
        while t + dt < tf-1e-10:
        
            f = []
            read_times = [0, self.a*dt, dt]
            for i in range(len(read_times)):
                read_data =  flux_WF_2_func(t + read_times[i])
                f.append(read_data)

            #(dt, u1, ug, f)
            u2, ug_new, _, err2 = self.solve_neumann_SDIRK2(dt,u2,ug_new,f)
            t += dt
            t2_new.append(t)
            ug_WF_new.append(np.copy(ug_new))
            ug_old = ug_new
            dt = self.get_new_dt_PI(dt, self.norm_inner(err2, 'N'), TOL_N)
            if dt < 1e-14:
                raise ValueError('too small timesteps, aborting')
        # final timestep
        dt = tf - t
        f = []
        read_times = [0, self.a*dt, dt]
        for i in range(len(read_times)):
            read_data =  flux_WF_2_func(t + read_times[i])
            f.append(read_data)

        #(dt, u1, ug, f)
        u2, ug_new, _, err2 = self.solve_neumann_SDIRK2(dt,u2,ug_new,f)
        t2_new.append(tf)
        ug_WF_new.append(np.copy(ug_new))
        # time-integration done

        # relaxation
        tmp = np.copy(ug_WF_old[-1])  # backup of old last value
        ug_WF_old = ug_WF_func(t2_new)  # interpolate old data to new grid

        WR_errors = [np.linalg.norm(
            ug_WF_new[-1] - ug_WF_old[-1])/np.linalg.norm(ug_WF_new[-1])]

        WR_error = WR_errors[-1]

        theta = self.DNWR_theta_opt_TA(t1, t2_new)
        ug_WF_old = [theta*ug_WF_new[i] +
                        (1-theta)*ug_WF_old[i] for i in range(len(t2_new))]
        # bookkeeping
        updates.append(WR_error)
        timesteps += len(t2_new) + len(t1) - 2
        t2_old = t2_new
        if updates[-1] < TOL_FP:  # STOPPING CRITERIA FOR FIXED POINT ITERATION
            print('converged', len(t1) - 1, len(t2_new) - 1)
            break
        
    results = kwargs.copy()
    results['tf'] = tf
    results['u1'] = u1.tolist()
    results['u2'] = u2.tolist()
    results['ug0'] = ug_WF_old[-1].tolist()
    results['iters'] = k+1
    results['residuals'] = updates
    results['timeGridDirichlet'] = t1
    results['timeGridNeumann'] = t2_new
    results['totalTimeSteps'] = timesteps

    with open("resultsRelaxation", 'w') as myfile:
        myfile.write(json.dumps(results, indent=2, sort_keys=True))



def runParticipant(self, dirichlet,init_cond, TOL, tf,nbrSteps=None, **kwargs):
    
    if self.WR_type != 'DNWR':
        raise ValueError('invalid solution method')

    TOL_D, TOL_N = TOL/5, TOL/5  # paper


    if dirichlet:
        time_stepper = self.solve_dirichlet_SDIRK2
        participant_name = 'Dirichlet'
        write_data_name = 'Heat-Flux'
        read_data_name = 'Temperature'
        mesh_name = 'Dirichlet-Mesh'

        u10, _, ug0 = self.get_initial_values(
            init_cond)
        self.r_old = TOL_D
        dt = self.get_dt0(tf, TOL_D, u10, which=1)
        domain = 'D'

    else:
        time_stepper = self.solve_neumann_SDIRK2
        participant_name = 'Neumann'
        read_data_name = 'Heat-Flux'
        write_data_name = 'Temperature'
        mesh_name = 'Neumann-Mesh'
        
        _, u10, ug0 = self.get_initial_values(
            init_cond)
        self.r_old = TOL_D
        dt = self.get_dt0(tf, TOL_N, u10, which=2)
        domain = 'N'

    flux0 = -self.lambda_diff*ug0-self.der@u10

    solver_process_index = 0
    solver_process_size = 1
    configuration_file_name = "../precice-config.xml"

    participant = precice.Participant(participant_name, configuration_file_name, solver_process_index, solver_process_size)

    dimensions = participant.get_mesh_dimensions(mesh_name)

    if dirichlet:
        read_data = ug0
        write_data = flux0
        
    else: 
        read_data = flux0
        write_data = ug0
    
    
    # Define mesh coordinates and register coordinates
    boundary_mesh = np.zeros([ug0.size, dimensions])
    boundary_mesh[:, 0] = 0  # x component
    boundary_mesh[:, 1] = np.linspace(0, 1, ug0.size)  # np.linspace(0, config.L, N+1)  # y component, leave blank

    vertex_ids =participant.set_mesh_vertices(mesh_name, boundary_mesh)
    

    if participant.requires_initial_data():
        participant.write_data(mesh_name, write_data_name, vertex_ids, write_data)

    participant.initialize()
    precice_dt = participant.get_max_time_step_size()

    ug = ug0
    u1 = u10
    Totaltimesteps = 0
    iters = 0
    t1 = [0]

    while participant.is_coupling_ongoing():
        if participant.requires_writing_checkpoint():
            ug0 = ug
            u10 = u1
            le0 = self.r_old
            dt0 = dt
        
        # compute time step size for this time step
        precice_dt = participant.get_max_time_step_size()
        
        # Ensures that we hit the end of the time window exactly
        if (precice_dt-dt<1e-10):
            dt = precice_dt
        

        read_times = [0, self.a*dt, dt]
        f = []

        for i in range(len(read_times)):
            read_data = participant.read_data(mesh_name, read_data_name, vertex_ids, read_times[i])
            f.append(read_data)


        #U2, ug_new, localu, flux_2
        u1, ug, write_data, le = time_stepper(dt, u1, ug, f)
        
        participant.write_data(mesh_name, write_data_name, vertex_ids, write_data)
        
        Totaltimesteps += 1
        t1.append(t1[-1]+dt)
        participant.advance(dt)

        dt = self.get_new_dt_PI(dt, self.norm_inner(
                le, domain), TOL_D)
        
        if participant.requires_reading_checkpoint():
            ug = ug0
            u1 = u10
            self.r_old = le0
            dt = dt0
            iters += 1
            t1 = [0]


    results = kwargs.copy()
    results['tf'] = tf
    results['uDomain'] = u1.tolist()
    results['ug'] = ug.tolist()
    results['iters'] = iters+1
    results['timeGrid'] = t1
    results['totalTimeSteps'] = Totaltimesteps

    print("../resultsQN"+ "_dir" + str(dirichlet))
    with open("../resultsQN" + "_dir" + str(dirichlet), 'w') as myfile:
        myfile.write(json.dumps(results, indent=2, sort_keys=True))
    
    participant.finalize()




if __name__ == '__main__':
    from FSI_verification import get_problem, get_solver, solve_monolithic
    from FSI_verification import get_parameters, get_init_cond
    import argparse


    parser = argparse.ArgumentParser(
    description='Solving heat equation for simple or complex interface case')
    parser.add_argument("-d", "--dirichlet", help="create a dirichlet problem", dest='dirichlet', action='store_true')
    parser.add_argument("-n", "--neumann", help="create a neumann problem", dest='neumann', action='store_true')
    parser.add_argument("-Tol", "--Tol", help="tolerance", default=1e-5,type=float)
    parser.add_argument("-which", "--which", metavar="material parameters", type=str, choices=['water', 'air', 'steel', 'water_steel','steel_water','air_water','air_steel'],
                    help="material parameters", default="steel")
    
    parser.add_argument("-relax", "--relax", help="toggels between QN and relaxation", dest='relax', action='store_true')
    parser.add_argument("-Tf", "--Tf", help="Tf", default=1e4,type=float)

    args = parser.parse_args()

    if args.dirichlet:
        dirichlet = True
    else:
        dirichlet = False
    
    init_cond_2d = get_init_cond(2, num=1)

    p_base = get_parameters('test')  # basic testing parameters
    save = 'verify/DNWR_TA/'

    print(args.which)
    pp = get_parameters(args.which)
    p2 = {'n': 100, 'dim': 2,'WR_type': 'DNWR', **pp}
    prob = get_problem(**p2)
    if not args.relax:
        prob.runParticipant(dirichlet,init_cond_2d, TOL=args.Tol, tf= args.Tf)
    else: 
        prob.runRelaxation(init_cond_2d, TOL=args.Tol, tf=args.Tf)