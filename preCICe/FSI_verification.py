# -*- coding: utf-8 -*-
"""
Created on Fri May  3 09:10:47 2019

@author: Peter Meisrimel, Lund University
"""

import time
import numpy as np
import pylab as pl
from Problem_FSI_1D import Problem_FSI_1D
from Problem_FSI_2D import Problem_FSI_2D
from numpy import sin, pi

pl.rcParams['lines.linewidth'] = 2
pl.rcParams['font.size'] = 14


def get_problem(dim=1, **kwargs):
    if dim == 1:
        return Problem_FSI_1D(**kwargs)
    elif dim == 2:
        return Problem_FSI_2D(**kwargs)
    else:
        raise ValueError('invalid dimension')


def get_solver(prob, order, WR_type='DNWR'):
    # method for solver selection
    
    if WR_type == 'DNWR':
        
        if order == 1:
            return prob.DNWR_IE
        elif order == 2:
            return prob.DNWR_SDIRK2
        elif order == 3:
            return prob.DNWR_SDIRK2_MP
        elif order == 4:
            return prob.DNWR_SDIRK2_rQN
        elif order == 5:
            return prob.DNWR_SDIRK2_QN
        elif order == 22:
            return prob.DNWR_SDIRK2_test
        
        elif order == -1:
            return prob.DNWR_SDIRK2_TA_single
        elif order == -2:
            return prob.DNWR_SDIRK2_TA_double
        elif order == -3:
            return prob.DNWR_SDIRK2_TA_rQN
        elif order == -4:
            return prob.DNWR_SDIRK2_TA_prQN
        elif order == -5:
            return prob.DNWR_SDIRK2_TA_short
        elif order == -6:
            return prob.DNWR_SDIRK2_TA_short_s
        elif order == -7:
            return prob.DNWR_SDIRK2_TA_short_my
        elif order == -8:
            return prob.DNWR_SDIRK2_TA_MQN
        elif order == -10:
            return prob.DNWR_SDIRK_FIXED
        elif order == -100:
            return prob.QN_full_error
        elif order == -200:
            return prob.DNWR_SDIRK2_prQN
        elif order == -666:
            return prob.DNWR_SDIRK2_TA_newrQN
        elif order == -999:           
            return prob.newfQN

    elif WR_type == 'NNWR':
        if order == 1:
            return prob.NNWR_IE
        elif order == 2:
            return prob.NNWR_SDIRK2

        elif order == -1:
            return prob.NNWR_SDIRK2_TA_single
        elif order == -2:
            return prob.NNWR_SDIRK2_TA_single  # should be double, but double is deprecated
    elif WR_type == 'MONOLITHIC':
        # to get proper monolithic solver for order = 22, 222
        order = abs(order) % 10
        if order == 1:
            return prob.Monolithic_IE
        elif order == 2:
            return prob.Monolithic_SDIRK2
    else:
        raise ValueError('order/method not available')


def get_parameters(which):
    # parameter selection
    lambda_air = 0.0243
    lambda_water = 0.58
    lambda_steel = 48.9

    alpha_air = 1.293*1005
    alpha_water = 999.7*4192.1
    alpha_steel = 7836*443
    if which == 'air':
        return {'alpha_1': alpha_air, 'alpha_2': alpha_air, 'lambda_1': lambda_air, 'lambda_2': lambda_air}
    elif which == 'steel':
        return {'alpha_1': alpha_steel, 'alpha_2': alpha_steel, 'lambda_1': lambda_steel, 'lambda_2': lambda_steel}
    elif which == 'water':
        return {'alpha_1': alpha_water, 'alpha_2': alpha_water, 'lambda_1': lambda_water, 'lambda_2': lambda_water}
    elif which == 'test':
        return {'alpha_1': 1., 'alpha_2': 1., 'lambda_1': 1, 'lambda_2': 1}
    elif which == 'all_1':
        return {'alpha_1': 1., 'alpha_2': 1., 'lambda_1': 1, 'lambda_2': 1}
    elif which == 'steel_water':
        return {'alpha_1': alpha_steel, 'alpha_2': alpha_water, 'lambda_1': lambda_steel, 'lambda_2': lambda_water}
    elif which == 'water_steel':
        return {'alpha_1': alpha_water, 'alpha_2': alpha_steel, 'lambda_1': lambda_water, 'lambda_2': lambda_steel}

    elif which == 'worst_case':
        return {'alpha_1': 1.0/10, 'alpha_2': 1., 'lambda_1': 10., 'lambda_2': 1.}
    elif which == 'water_air':
        return {'alpha_1': alpha_water, 'alpha_2': alpha_air, 'lambda_1': lambda_water, 'lambda_2': lambda_air}
    elif which == 'steel_air':
        return {'alpha_1': alpha_steel, 'alpha_2': alpha_air, 'lambda_1': lambda_steel, 'lambda_2': lambda_air}
    elif which == 'unstable_test':
        return {'alpha_1': 0.01, 'alpha_2': 0.01, 'lambda_1': 0.001, 'lambda_2': 0.001}


def get_init_cond(dim, extra_len=False, num=1):
    if extra_len:
        if num == 1:
            if dim == 1:
                return lambda x: 500*sin(pi/10*(x+9))
            elif dim == 2:
                return lambda x, y: 500*sin(pi*y)*sin((pi/10)*(x + 9))
        elif num == 2:
            if dim == 1:
                return lambda x: 500*sin(pi/5*(x+2))
            elif dim == 2:
                return lambda x, y: 500*sin(pi*y)*sin((pi/5)*(x + 2))
    else:
        if num == 1:
            if dim == 1:
                return lambda x: 500*sin(pi/2*(x+1))
            elif dim == 2:
                return lambda x, y: 500*sin(pi*y)*sin((pi/2)*(x + 1))
        elif num == 2:
            if dim == 2:
                return lambda x, y: 800*sin(pi*y)*sin(pi*(x + 1))**2
    raise ValueError('no initial cond available for this input')


def solve_monolithic(tf=1, N_steps=20, init_cond=None, order=1, **kwargs):
    # monolithic solver
    prob = get_problem(WR_type='MONOLITHIC', **kwargs)

    solver = get_solver(prob, order, WR_type='MONOLITHIC')
    res = solver(tf, N_steps, init_cond)
    return (*res, prob)


def ex_sol_grid(n=30, tf=1, len_1=1, len_2=1, ex_sol=None, dim=2, **kwargs):
    # evalutes a given ex_sol function on a grid matching the discretization given via "n"
    if dim == 1:
        ref_sol = np.zeros(((len_1 + len_2)*(n + 1) - 1))
        xx = np.linspace(-len_1, len_2, (len_1 + len_2)*(n + 1) + 1)
        for i, x in enumerate(xx[1:-1]):
            ref_sol[i] = ex_sol(x, tf)
        ref1 = ref_sol[:(len_1*(n + 1) - 1)]
        ref2 = ref_sol[-(len_2*(n + 1) - 1):]
        refg = ref_sol[(len_1*(n + 1) - 1):-(len_2*(n + 1) - 1)]
    elif dim == 2:
        ref_sol = np.zeros(n*((len_1 + len_2)*(n + 1) - 1))
        xx = np.linspace(-len_1, len_2, (len_1 + len_2)*(n + 1) + 1)
        yy = np.linspace(0, 1, n + 2)
        for i, x in enumerate(xx[1:-1]):
            for j, y in enumerate(yy[1:-1]):
                ref_sol[i*n + j] = ex_sol(x, y, tf)
        ref1 = ref_sol[:n*(len_1*(n + 1) - 1)]
        ref2 = ref_sol[-n*(len_2*(n + 1) - 1):]
        refg = ref_sol[n*(len_1*(n + 1) - 1):-n*(len_2*(n + 1) - 1)]
    return ref1, ref2, refg

# verifiy order of space discretization by picking a sufficiently fine grid in time and an exact solution


def verify_space_error(tf=1, init_cond=None, n_min=2, N_steps=100, k=8, ex_sol=None, savefig=None, **kwargs):
    if kwargs['lambda_1'] != kwargs['lambda_2']:
        raise ValueError('only works for identical lambda')
    if kwargs['alpha_1'] != kwargs['alpha_2']:
        raise ValueError('only works for identical alpha')

    errs = []

    n_list = np.array([n_min*(2**i) for i in range(k)])
    for n in n_list:
        # L2 factor for 2D case, inner points
        ref1, ref2, refg = ex_sol_grid(n=n, tf=tf, ex_sol=ex_sol, **kwargs)

        u1, u2, ug, flux, prob = solve_monolithic(
            tf, N_steps, init_cond, order=2, n=n, **kwargs)
        errs.append(prob.norm_inner(ref1 - u1, ref2 - u2, refg - ug))
        n *= 2

    pl.figure()
    pl.loglog(n_list, errs, label='u', marker='o')
    pl.loglog(n_list, 1/n_list, label='1st', linestyle='--')
    pl.loglog(n_list, 1/(n_list**2), label='2nd', linestyle='--')
    pl.legend()
    pl.xlabel('gridsize')
    pl.ylabel('err')
    pl.grid(True, which='major')
    pl.title('error in space')
    if savefig is not None:
        s = 'err_space_tf_{}_steps_{}_dim_{}.png'.format(
            tf, N_steps, kwargs['dim'])
        pl.savefig(savefig + s, dpi=100)
    print(errs)

# verify time-integration order of monolithic solution with itself


def verify_mono_time(tf=1, init_cond=None, order=1, k=5, savefig=None, **kwargs):
    u1_ref, u2_ref, ug_ref, _, prob = solve_monolithic(
        tf, 2**(k+1), init_cond, order, **kwargs)

    errs = []
    steps = [2**i for i in range(k)]
    for s in steps:
        u1, u2, ug, _, _ = solve_monolithic(tf, s, init_cond, order, **kwargs)
        errs.append(prob.norm_inner(u1_ref - u1, u2_ref - u2, ug_ref - ug))
    for i in range(k-1):
        print(np.log2(errs[i]/errs[i+1]))

    pl.figure()
    dts = [tf/s for s in steps]
    pl.loglog(dts, errs, label='u', marker='o')
    pl.loglog(dts, dts, label='1 st order', linestyle='--')
    pl.loglog(dts, [t**2 for t in dts], label='2 nd order', linestyle='--')
    pl.legend()
    pl.xlabel('dt')
    pl.ylabel('Err')
    pl.grid(True, which='major')
    pl.title('time-integration error, monolithic')
    if savefig is not None:
        s = 'mono_time_tf_{}_ord_{}_dim_{}.png'.format(
            tf, order, kwargs['dim'])
        pl.savefig(savefig + s, dpi=100)

# verify convergence of coupling scheme for decreasing tolerances with monolithic solution, for fixed delta t


def verify_with_monolithic(tf=1, N_steps=20, init_cond=None, order=1, k=10, theta=None, WR_type='DNWR', savefig=None, **kwargs):
    if WR_type == 'NNWR':
        from mpi4py import MPI
        comm = MPI.COMM_WORLD
        if comm.size != 2:
            raise ValueError(
                'incorrect number of processes, needs to be exactly 2')
        ID_SELF = comm.rank

    prob = get_problem(WR_type=WR_type, **kwargs)
    solver = get_solver(prob, order, WR_type)

    if WR_type == 'NNWR' and ID_SELF == 1:
        pass
    else:
        u1_ref, u2_ref, ug_ref, _, prob_mono = solve_monolithic(
            tf, N_steps, init_cond, 2, **kwargs)
    if WR_type == 'NNWR':
        comm.Barrier()  # sync, only one process calculates monolithic solution

    if WR_type == 'NNWR' and ID_SELF == 1:
        tols = [10**(-i) for i in range(k)]
        for tol in tols:
            solver(tf, N_steps, N_steps, init_cond, theta, TOL=tol)
        return None
    # else: serial DNWR case and ID_SELF == 0 for NNWR

    errs = {'u': [], 'it': []}
    tols = [10**(-i) for i in range(k)]
    for tol in tols:
        u1, u2, ug, E, it = solver(
            tf, N_steps, 1, 1, init_cond, theta, TOL=tol)
        errs['u'].append(prob_mono.norm_inner(
            u1_ref - u1, u2_ref - u2, ug_ref - ug))
        errs['it'].append(it)
    for i in range(k-1):
        print(np.log10(errs['u'][i]/errs['u'][i+1]))

    pl.figure()
    pl.loglog(tols, errs['u'], label='u', marker='o')
    pl.loglog(tols, tols, label='1 st order', linestyle='--')
    pl.loglog(tols, [t**2 for t in tols], label='2 nd order', linestyle='--')
    pl.title('Verification with monolithic solution')
    pl.legend()
    pl.xlabel('TOL')
    pl.ylabel('Err')
    pl.grid(True, which='major')
    if savefig is not None:
        s = 'verify_mono_time_steps_{}_dim_{}_ord_{}.png'.format(
            N_steps, kwargs['dim'], order)
        pl.savefig(savefig + s, dpi=100)

    pl.figure()
    pl.semilogx(tols, errs['it'], label='iterations', marker='o')
    pl.legend()
    pl.xlabel('TOL')
    pl.ylabel('DN iter')
    pl.title('Verification with monolithic solution')
    pl.grid(True, which='major')
    if savefig is not None:
        s = 'verify_mono_time_iter_steps_{}_dim_{}_ord_{}.png'.format(
            N_steps, kwargs['dim'], order)
        pl.savefig(savefig + s, dpi=100)

# verify "order" of splitting error by calculating it for fixed, small tolerance and increasing number of timesteps


def verify_splitting_error(init_cond, tf=1, k=10, kmin=0, TOL=1e-12, theta=None, WR_type='DNWR', order=1, savefig=None, **kwargs):
    if WR_type == 'NNWR':
        from mpi4py import MPI
        comm = MPI.COMM_WORLD
        if comm.size != 2:
            raise ValueError(
                'incorrect number of processes, needs to be exactly 2')
        ID_SELF = comm.rank

    prob = get_problem(WR_type=WR_type, **kwargs)
    solver = get_solver(prob, order, WR_type)

    if WR_type == 'NNWR' and ID_SELF == 1:
        for n_steps in [2**i for i in range(kmin, k)]:
            comm.Barrier()
            solver(tf, n_steps, n_steps, init_cond, theta, TOL=1e-13)
        return None

    dts = []
    errs = {'u': [], 'it': []}
    for n_steps in [2**i for i in range(kmin, k)]:
        u1_ref, u2_ref, ug_ref, _, prob_mono = solve_monolithic(
            tf, n_steps, init_cond, 2, **kwargs)
        if WR_type == 'NNWR':
            comm.Barrier()
        dts.append(tf/n_steps)
        u1, u2, ug, E, it = solver(
            tf, n_steps, n_steps, init_cond, theta, TOL=1e-13)
        errs['u'].append(prob_mono.norm_inner(
            u1_ref - u1, u2_ref - u2, ug_ref - ug))
        errs['it'].append(it)
    for i in range(k-1-kmin):
        print(np.log2(errs['u'][i]/errs['u'][i+1]))

    pl.figure()
    pl.loglog(dts, errs['u'], label='u', marker='o')
    pl.loglog(dts, dts, label='1 st order', linestyle='--')
    pl.loglog(dts, [t**2 for t in dts], label='2 nd order', linestyle='--')
    pl.title('Splitting Error')
    pl.legend()
    pl.xlabel('dt')
    pl.ylabel('Err')
    pl.grid(True, which='major')
    if savefig is not None:
        s = 'splitting_error_dim_{}_ord_{}.png'.format(kwargs['dim'], order)
        pl.savefig(savefig + s, dpi=100)

    pl.figure()
    pl.semilogx(dts, errs['it'], label='iterations', marker='o')
    pl.legend()
    pl.title('Splitting Error')
    pl.xlabel('dt')
    pl.ylabel('DN iter')
    pl.grid(True, which='major')
    if savefig is not None:
        s = 'splitting_error_iters_dim_{}_ord_{}.png'.format(
            kwargs['dim'], order)
        pl.savefig(savefig + s, dpi=100)

# sum of splitting and time-integration order
# calculating time-integration error( + splitting error) for a small tolerance


def verify_comb_error(init_cond, tf=1, k=10, kmin=0, theta=None, WR_type='DNWR', order=1, savefig=None, **kwargs):
    if WR_type == 'NNWR':
        from mpi4py import MPI
        comm = MPI.COMM_WORLD
        if comm.size != 2:
            raise ValueError(
                'incorrect number of processes, needs to be exactly 2')
        ID_SELF = comm.rank

    prob = get_problem(WR_type=WR_type, **kwargs)
    solver = get_solver(prob, order, WR_type)

    if WR_type == 'NNWR' and ID_SELF == 1:
        pass
    else:
        u1_ref, u2_ref, ug_ref, _, prob_mono = solve_monolithic(
            tf, 2**(k+1), init_cond, order, **kwargs)
    if WR_type == 'NNWR':
        comm.Barrier()  # sync, only one process claculates monolithic sol

    if WR_type == 'NNWR' and ID_SELF == 1:
        for n_steps in [2**i for i in range(kmin, k)]:
            solver(tf, n_steps, n_steps, init_cond, theta, TOL=1e-13)
        return None

    dts = []
    errs = {'u': [], 'it': []}
    for n_steps in [2**i for i in range(kmin, k)]:
        dts.append(tf/n_steps)
        u1, u2, ug, E, it = solver(
            tf, n_steps, n_steps, init_cond, theta, TOL=1e-13)
        errs['u'].append(prob_mono.norm_inner(
            u1_ref - u1, u2_ref - u2, ug_ref - ug))
        errs['it'].append(it)
    for i in range(k-1-kmin):
        print(np.log2(errs['u'][i]/errs['u'][i+1]))

    pl.figure()
    pl.loglog(dts, errs['u'], label='u', marker='o')
    pl.loglog(dts, dts, label='1 st order', linestyle='--')
    pl.loglog(dts, [t**2 for t in dts], label='2 nd order', linestyle='--')
    pl.legend()
    pl.title('Splitting + time int error test')
    pl.xlabel('dt')
    pl.ylabel('Err')
    pl.grid(True, which='major')
    if savefig is not None:
        s = 'verify_comb_error_dim_{}_ord_{}.png'.format(kwargs['dim'], order)
        pl.savefig(savefig + s, dpi=100)

    pl.figure()
    pl.semilogx(dts, errs['it'], label='iterations', marker='o')
    pl.legend()
    pl.xlabel('dt')
    pl.ylabel('DN iter')
    pl.title('Splitting + time int error test')
    pl.grid(True, which='major')
    if savefig is not None:
        s = 'verify_comb_error_iters_dim_{}_ord_{}.png'.format(
            kwargs['dim'], order)
        pl.savefig(savefig + s, dpi=100)

# same as verify_comb_error, but now also for multirate:
# coarse-coarse, coarse-fine, fine-coarse, C = refinement factor


def verify_MR_comb(init_cond, tf=1, k=12, kmin=0, theta=None, WR_type='DNWR', order=1, savefig=None, C=10, TOL=1e-13, **kwargs):
    assert (type(C) is int)
    if WR_type == 'NNWR':
        from mpi4py import MPI
        comm = MPI.COMM_WORLD
        if comm.size != 2:
            raise ValueError(
                'incorrect number of processes, needs to be exactly 2')
        ID_SELF = comm.rank

    prob = get_problem(WR_type=WR_type, **kwargs)
    solver = get_solver(prob, order, WR_type)

    u1_ref, u2_ref, ug_ref, _, prob_mono = solve_monolithic(
        tf, C*2**(k+1), init_cond, 2, **kwargs)

    dts = []
    errs_cc = {'u': [], 'it': []}
    errs_cf = {'u': [], 'it': []}
    errs_fc = {'u': [], 'it': []}
    for n_steps in [2**i for i in range(kmin, k)]:
        dts.append(tf/n_steps)
        # coarse-coarse
        u1, u2, ug, E, it = solver(
            tf, n_steps, 1, 1, init_cond, theta, TOL=TOL)
        errs_cc['u'].append(prob_mono.norm_inner(
            u1_ref - u1, u2_ref - u2, ug_ref - ug))
        errs_cc['it'].append(it)

        # coarse-fine
        u1, u2, ug, E, it = solver(
            tf, n_steps, 1, C, init_cond, theta, TOL=TOL)
        errs_cf['u'].append(prob_mono.norm_inner(
            u1_ref - u1, u2_ref - u2, ug_ref - ug))
        errs_cf['it'].append(it)

        # fine-coarse
        u1, u2, ug, E, it = solver(
            tf, n_steps, C, 1, init_cond, theta, TOL=TOL)
        errs_fc['u'].append(prob_mono.norm_inner(
            u1_ref - u1, u2_ref - u2, ug_ref - ug))
        errs_fc['it'].append(it)

    pl.figure()
    pl.loglog(dts, errs_cc['u'], label='c-c', marker='o')
    pl.loglog(dts, errs_cf['u'], label='c-f', marker='d', linestyle=':')
    pl.loglog(dts, errs_fc['u'], label='f-c', marker='+')
    pl.loglog(dts, dts, label='1 st order', linestyle='--')
    pl.loglog(dts, [t**2 for t in dts], label='2 nd order', linestyle='--')
    pl.legend()
    pl.title('MR error test')
    pl.xlabel('dt')
    pl.ylabel('Err')
    pl.grid(True, which='major')
    if savefig is not None:
        s = 'verify_MR_error_dim_{}_ord_{}_C_{}.png'.format(
            kwargs['dim'], order, C)
        pl.savefig(savefig + s, dpi=100)

    pl.figure()
    pl.semilogx(dts, errs_cc['it'], label='c-c', marker='o')
    pl.semilogx(dts, errs_cf['it'], label='c-f', marker='d')
    pl.semilogx(dts, errs_fc['it'], label='f-c', marker='+')
    pl.legend()
    pl.xlabel('dt')
    pl.ylabel('DN iter')
    pl.title('MR error test')
    pl.grid(True, which='major')
    if savefig is not None:
        s = 'verify_MR_error_iters_dim_{}_ord_{}.png'.format(
            kwargs['dim'], order)
        pl.savefig(savefig + s, dpi=100)

    cc_approx_order = [np.log2(errs_cc['u'][i]/errs_cc['u'][i+1])
                       for i in range(kmin, k-1)]
    cf_approx_order = [np.log2(errs_cf['u'][i]/errs_cf['u'][i+1])
                       for i in range(kmin, k-1)]
    fc_approx_order = [np.log2(errs_fc['u'][i]/errs_fc['u'][i+1])
                       for i in range(kmin, k-1)]
    pl.figure()
    pl.title('approximate orders')
    pl.semilogx(dts[:-1], cc_approx_order, label='c-c')
    pl.semilogx(dts[:-1], cf_approx_order, label='c-f')
    pl.semilogx(dts[:-1], fc_approx_order, label='f-c')
    pl.axhline(1, linestyle='--', label='1st')
    pl.axhline(2, linestyle=':', label='2nd')
    pl.ylim(-1, 3)
    pl.xlabel('dt')
    pl.legend()
    if savefig is not None:
        s = 'verify_MR_approx_ord_dim_{}_ord_{}.png'.format(
            kwargs['dim'], order)
        pl.savefig(savefig + s, dpi=100)

# verify time-itegration order of coupling scheme by comparison with monolithic solution for fixed, small tolerance and increasing number of timesteps


def verify_test(init_cond, tf=1, k=10, kmin=0, theta=None, WR_type='DNWR', order=1, savefig=None, **kwargs):
    if WR_type == 'NNWR':
        raise ValueError('no NNWR here')

    prob = get_problem(WR_type=WR_type, **kwargs)
    solver = get_solver(prob, order, WR_type)

    u1_ref, u2_ref, ug_ref, _, prob_mono = solve_monolithic(
        tf, 2**(k+1), init_cond, order, **kwargs)

    dts, errs_time, errs_split = [], [], []
    for n_steps in [2**i for i in range(kmin, k)]:
        u1_mono, u2_mono, ug_mono, _, _ = solve_monolithic(
            tf, n_steps, init_cond, order, **kwargs)
        errs_time.append(prob_mono.norm_inner(
            u1_ref - u1_mono, u2_ref - u2_mono, ug_ref - ug_mono))

        dts.append(tf/n_steps)
        u1, u2, ug, E, it = solver(
            tf, n_steps, n_steps, init_cond, theta, TOL=1e-13)
        errs_split.append(prob_mono.norm_inner(
            u1_mono - u1, u2_mono - u2, ug_mono - ug))

    pl.figure()
    pl.loglog(dts, errs_time, label='time', marker='o', linestyle='-')
    pl.loglog(dts, errs_split, label='split', marker='o', linestyle='-')
    pl.legend()
    pl.title('Splitting + time int error test')
    pl.xlabel('dt')
    pl.ylabel('Err')
    pl.grid(True, which='major')
    if savefig is not None:
        s = 'testing_dim_{}_ord_{}.png'.format(kwargs['dim'], order)
        pl.savefig(savefig + s, dpi=100)

# verify correctness of adaptive coupling scheme via comparison with monolithic (fixed number of steps, many) and decreasing tolerances


def verify_adaptive(init_cond, tf=1e4, k_ref=10, k=10, WR_type='DNWR', which_ref='fine', order=-2, savefig=None, **kwargs):
    if WR_type == 'NNWR':
        from mpi4py import MPI
        comm = MPI.COMM_WORLD
        if comm.size != 2:
            raise ValueError(
                'incorrect number of processes, needs to be exactly 2')
        ID_SELF = comm.rank

    prob = get_problem(WR_type=WR_type, **kwargs)
    solver = get_solver(prob, order, WR_type)

    if WR_type == 'NNWR' and ID_SELF == 1:
        if which_ref == 'fixed':
            pass
        elif which_ref == 'fine':
            solver(tf, init_cond, TOL=10**(-k))
    else:  # DNWR or ID_SELF == 0
        if which_ref == 'fixed':
            u1_ref, u2_ref, ug_ref, _, prob_norm = solve_monolithic(
                tf, 2**k_ref, init_cond, order=order, **kwargs)
        elif which_ref == 'fine':
            u1_ref, u2_ref, ug_ref, _, _, _ = solver(
                tf, init_cond, TOL=10**(-k))
            prob_norm = get_problem(WR_type='MONOLITHIC', **kwargs)
        else:
            raise KeyError(
                'invalid which_ref input, needs to be either fixed or fine')

    tols = np.array([10**(-i) for i in range(k)])

    if WR_type == 'NNWR' and ID_SELF == 1:
        for tol in tols:
            solver(tf, init_cond, TOL=tol)
        return None

    # else, also serial

    errs = {'u': [], 'it': [], 'steps': []}
    for tol in tols:
        u1, u2, ug, E, it, s = solver(tf, init_cond, TOL=tol)
        errs['u'].append(prob_norm.norm_inner(
            u1_ref - u1, u2_ref - u2, ug_ref - ug))
        errs['it'].append(it)
        errs['steps'].append(s)
    for i in range(k-1):
        print(np.log10(errs['u'][i]/errs['u'][i+1]))

    pl.figure()
    pl.loglog(tols, errs['u'], label='u', marker='o')
    pl.loglog(tols, tols, label='1 st order', linestyle='--')
    pl.loglog(tols, tols**(1/2), label='order 1/2', linestyle=':')
    pl.legend()
    pl.grid(True, which='major')
    pl.title('Adaptive verification')
    pl.xlabel('TOL')
    pl.ylabel('Err')
    if savefig is not None:
        s = 'verify_adaptive_dim_{}_n_{}_order_{}.png'.format(
            kwargs['dim'], kwargs['n'], order)
        pl.savefig(savefig + s, dpi=100)

    pl.figure()
    pl.semilogx(tols, errs['it'], label='iterations', marker='o')
    pl.legend()
    pl.xlabel('TOL')
    pl.ylabel('DN iter')
    pl.grid(True, which='major')
    pl.title('Adaptive verification')
    if savefig is not None:
        s = 'verify_adaptive_iters_dim_{}_n_{}_order_{}.png'.format(
            kwargs['dim'], kwargs['n'], order)
        pl.savefig(savefig + s, dpi=100)

    pl.figure()
    pl.loglog(tols, errs['steps'], label='timesteps', marker='o')
    pl.loglog(tols, tols**(-1/2), label='order 1/2', linestyle='--')
    pl.loglog(tols, 1/tols, label='order 1', linestyle=':')
    pl.legend()
    pl.xlabel('TOL')
    pl.ylabel('steps')
    pl.grid(True, which='major')
    pl.title('Adaptive verification')
    if savefig is not None:
        s = 'verify_adaptive_timesteps_dim_{}_n_{}_order_{}.png'.format(
            kwargs['dim'], kwargs['n'], order)
        pl.savefig(savefig + s, dpi=100)

# simply plot the solution


def visual_verification(init_cond, tf=1, N_steps=20, TOL=1e-14, order=1, theta=None, WR_type='DNWR', savefig=None, len_1=1, len_2=1, **kwargs):
    if WR_type == 'NNWR':
        from mpi4py import MPI
        comm = MPI.COMM_WORLD
        if comm.size != 2:
            raise ValueError(
                'incorrect number of processes, needs to be exactly 2')
        ID_SELF = comm.rank

    prob = get_problem(WR_type=WR_type, len_1=len_1, len_2=len_2, **kwargs)
    solver = get_solver(prob, order, WR_type)

    if order in [1, 2, 22]:
        sol = solver(tf, N_steps, N_steps, init_cond, theta, TOL=TOL)
    elif order in [-2, -22]:
        sol = solver(tf, init_cond, TOL=TOL)
    else:
        raise ValueError('invalid order')

    if WR_type == 'NNWR' and ID_SELF == 1:
        return None  # plotting only on first processor

    u1, u2, ug = sol[:3]

    dim, n = kwargs['dim'], kwargs['n']

    fig = pl.figure()
    if dim == 1:
        res = np.hstack((np.array([0.]), u1, ug, u2, np.array([0.])))
        pl.plot(np.linspace(-len_1, len_2, (len_1 + len_2)
                * (n+1) + 1), res, label='solution')
        pl.axvline(0, color='red', linestyle='--', label='interface')
        pl.xlabel('x')
        pl.ylabel('u')
        pl.legend()
    elif dim == 2:
        res = np.zeros((n + 2, (len_1 + len_2)*(n+1) + 1))
        res[1:n+1, 1:(len_1 * (n+1) + 1) - 1] = np.reshape(u1,
                                                           (len_1*(n+1) - 1, n)).T
        res[1:n+1, (len_1 * (n+1) + 1) - 1] = ug
        res[1:n+1, -(len_2 * (n+1)):-1] = np.reshape(u2,
                                                     (len_2*(n+1) - 1, n)).T
        p = pl.pcolor(res)
        fig.colorbar(p)
    else:
        raise ValueError('invalid dimension')

    if savefig is not None:
        s = 'visial_verifiy_{}_{}.png'.format(dim, kwargs['n'])
        pl.savefig(savefig + s, dpi=100)


def QN_error(init_cond, tf=1, k=12, kmin=0, C1=1, C2=1, thing=4, QN=True, theta=None, WR_type='DNWR', order=1, savefig=None, C=10, TOL=1e-13, which="test", **kwargs):
    assert (type(C) is int)

    dts = []
    errs_cc = {'u_h': [], 'u_m': [], 'u_l': [],
               'it_h': [], 'it_l': [], 'it_m': []}
    errs_cf = {'u': [], 'it': []}
    errs_fc = {'u': [], 'it': []}
    for s in [2**(i+2) for i in range(kmin, k)]:

        dts.append(s)
        init_cond_2d = get_init_cond(2)
        pp = get_parameters(which)
        p2 = {'n': 20, 'dim': 2, **pp}

        prob = get_problem(WR_type='DNWR', **p2)
        # iter_matrix = prob.compute_iteration_matrix_two_step(tf/2).toarray()
        # print(iter_matrix)
        # pl.figure()
        # pl.imshow(np.log(np.abs(iter_matrix)))
        # pl.colorbar()
        # pl.show()

        solver = get_solver(prob, thing, WR_type)

        u1_ref, u2_ref, ug_ref, _, prob_mono = solve_monolithic(
            tf, 1, init_cond, 2, **p2)

        u1, u2, ug, E, it = solver(
            tf, C1, C2, init_cond, theta, QN=QN, TOL=1e-10)
        print(QN)
    #     errs_cc['u_h'].append(prob_mono.norm_inner(
    #         u1_ref - u1, u2_ref - u2, ug_ref - ug))
    #     errs_cc['it_h'].append(it)

    # pl.figure()
    # pl.loglog(dts, errs_cc['u_h'], label='TOL_G 1e-7', marker='o')
    # pl.legend()
    # pl.title('Dn iteration error')
    # pl.xlabel('number of elements')
    # pl.ylabel('Err')
    # pl.grid(True, which='major')
    # if savefig is not None:
    #     s = 'tol_subsolver_{}_ord_{}_C_{}.png'.format(kwargs['dim'], order, C)
    #     pl.savefig(savefig + s, dpi=100)


def QN_error2(init_cond, tf=1, k=12, kmin=0, C1=1, C2=1, thing=4, QN=True, theta=None, WR_type='DNWR', order=1, savefig=None, C=10, TOL=1e-13, which="test", **kwargs):
    assert (type(C) is int)

    dts = []
    errs_cc = {'u_h': [], 'u_m': [], 'u_l': [],
               'it_h': [], 'it_l': [], 'it_m': []}
    errs_cf = {'u': [], 'it': []}
    errs_fc = {'u': [], 'it': []}
    init_cond_2d = get_init_cond(2)
    pp = get_parameters(which)

    # p1 = {'init_cond': init_cond_1d, 'n': 50, 'dim': 1, 'order': 2, 'WR_type': 'DNWR', **pp, 'tf': 10000}
    p2 = {'n': 50, 'dim': 2, **pp}
    # -10 rQNWR
    # -2 TA QNWR
    prob = get_problem(WR_type='DNWR', **p2)
    solver = get_solver(prob, -10, WR_type)

    u1, u2, ug, E, it, _, _ = solver(tf, init_cond, TOL=1e-4)


def compare_rQN_QN_TA(init_cond, tf=1, k=12, kmin=0, C1=1, C2=1, thing=4, QN=True, theta=None, WR_type='DNWR', order=1, savefig=None, C=10, TOL=1e-13, which="test", **kwargs):
    assert (type(C) is int)
    
    dts = []
    errs_cc = {'u_h': [], 'u_m': [], 'u_l': [],
               'it_h': [], 'it_l': [], 'it_m': []}
    errs_cf = {'u': [], 'it': []}
    errs_fc = {'u': [], 'it': []}
    init_cond_2d = get_init_cond(2)
    pp = get_parameters(which)

    p2 = {'n': 20, 'dim': 2, **pp}

    # u1_ref, u2_ref, ug_ref, _, prob_mono = solve_monolithic(
    #     # tf, 1, init_cond, 2, **p2)

    # -10 rQNWR
    # -2 TA QNWR
    prob = get_problem(WR_type='DNWR', **p2)
    #new solver -666
    #new solver full QN -999
    solver = get_solver(prob, -999, WR_type)
    u1T, u2T, ugT, E, it, _, _ = solver(tf, init_cond, TOL=1e-4)
    print(np.linalg.norm(ugT))

    eQN = []
    erQN = []
    timeQN = []
    timerQN = []

    tols = [1e-5, 1e-6, 1e-7]

    # for tol in tols:
    #     prob = get_problem(WR_type='DNWR', **p2)
    #     solver = get_solver(prob, -2, WR_type)
    #     t0 = time.time()
    #     u1QN, u2QN, ugQN, E, it, _, _ = solver(tf, init_cond, TOL=tol)
    #     timeQN.append(time.time()-t0)
    #     eQN.append(prob_mono.norm_inner(u1QN - u1T, u2QN - u2T, ugQN - ugT))

    # for tol in tols:
    #     prob = get_problem(WR_type='DNWR', **p2)
    #     solver = get_solver(prob, -4, WR_type)

    #     t0 = time.time()
    #     u1rQN, u2rQN, ugrQN, E, it, _ = solver(
    #         tf, init_cond, TOL=tol, maxiter=20)
    #     timerQN.append(time.time()-t0)
    #     erQN.append(prob_mono.norm_inner(
    #         u1rQN - u1T, u2rQN - u2T, ugrQN - ugT))

    # pl.figure()
    # pl.loglog(tols, eQN, label='QN', marker='o')
    # pl.loglog(tols, erQN, label='rQN', marker='+')
    # pl.legend()
    # pl.title('Error of the last time step')
    # pl.xlabel('Tol')
    # pl.ylabel('Err')
    # pl.grid(True, which='major')
    # s = 'ErrorVsTolQN{}_{}.png'.format(tf, which)
    # pl.savefig(s, dpi=100)

    # pl.figure()
    # pl.loglog(tols, timeQN, label='QN', marker='o')
    # pl.loglog(tols, timerQN, label='rQN', marker='+')
    # pl.legend()
    # pl.title('Runtime')
    # pl.xlabel('Tol')
    # pl.ylabel('Seconds')
    # pl.grid(True, which='major')
    # s = 'RuntimeVsTolQN{}_{}.png'.format(tf, which)
    # pl.savefig(s, dpi=100)


def QN_error_Coupling(init_cond, tf=1, k=12, kmin=0, C1=1, C2=1, thing=-10, QN=True, theta=None, WR_type='DNWR', order=1, savefig=None, C=10, TOL=1e-13, which="test", **kwargs):
    assert (type(C) is int)

    dts = []
    errs_cc = {'u_h': [], 'u_m': [], 'u_l': [],
               'it_h': [], 'it_l': [], 'it_m': []}
    errs_cf = {'u': [], 'it': []}
    errs_fc = {'u': [], 'it': []}
    init_cond_2d = get_init_cond(2)
    pp = get_parameters(which)
    # p1 = {'init_cond': init_cond_1d, 'n': 50, 'dim': 1, 'order': 2, 'WR_type': 'DNWR', **pp, 'tf': 10000}
    p2 = {'n': 20, 'dim': 2, **pp}
    prob = get_problem(WR_type='DNWR', **p2)
    ug_l = []

    u1_ref, u2_ref, ug_ref, _, prob_mono = solve_monolithic(
        tf, 1, init_cond, 2, **p2)

    solver = get_solver(prob, 4, WR_type)
    u1RQN, u2RQN, ugRQN, E, it = solver(
        tf, C1, C2, init_cond, theta, QN=QN, TOL=1e-8)

    solver = get_solver(prob, 5, WR_type)
    u1QN, u2QN, ugQN, E, it = solver(
        tf, C1, C2, init_cond, theta, QN=QN, TOL=1e-10)

    print(ugRQN)
    print(ugQN)
    print(np.linalg.norm(ugRQN-ugQN))
