# -*- coding: utf-8 -*-
"""
Created on Fri May  3 09:10:47 2019

@author: Peter Meisrimel with code basis of Azahar Monge
"""

import numpy as np
from scipy.interpolate import interp1d


class Problem_FSI:
    a, ahat = 1 - (1/2)*np.sqrt(2), 2 - (5/4)*np.sqrt(2)
    # len_1, len_2 are lengthes of left/right parts of the subdomain, only integer values allowed for now

    def __init__(self, n=10, lambda_1=0, lambda_2=0, alpha_1=0, alpha_2=0, WR_type='DNWR', len_1=1, len_2=1):
        if type(len_1) is not int:
            raise ValueError('len_1 must be integer valued (for now)')
        if type(len_2) is not int:
            raise ValueError('len_2 must be integer valued (for now)')
        self.n = n
        self.ny = self.n**(self.dim - 1)
        self.dx = 1/(self.n + 1)
        self.lambda_1, self.lambda_2 = lambda_1, lambda_2
        self.alpha_1, self.alpha_2 = alpha_1, alpha_2
        self.len_total = len_1 + len_2  # required for discrete L2 norm

        self.WR_type = WR_type
        if self.WR_type == 'DNWR' or self.WR_type == 'MONOLITHIC':
            self.len_1, self.len_2 = int(len_1), int(len_2)
            # number of internal unknowns on domain i
            self.n_int_1 = ((n + 1)*self.len_1 - 1)*self.ny
            self.n_int_2 = ((n + 1)*self.len_2 - 1)*self.ny
            self.A1, self.M1, self.A1g, self.Ag1, self.Agg1, self.M1g, self.Mg1, self.Mgg1 = self.compute_matrices(
                len_1*(n+1) - 1, n, self.alpha_1, self.lambda_1, 'right', neumann=False)
            self.A2, self.M2, self.A2g, self.Ag2, self.Agg2, self.M2g, self.Mg2, self.Mgg2, self.Neumann_A, self.Neumann_M = self.compute_matrices(
                len_2*(n+1) - 1, n, self.alpha_2, self.lambda_2, 'left', neumann=True)
        elif self.WR_type == 'NNWR':
            from mpi4py import MPI
            self.comm = MPI.COMM_WORLD
            self.ID_SELF = self.comm.rank
            self.ID_OTHER = (self.ID_SELF + 1) % self.comm.size
            self.TAG_TIMES, self.TAG_DATA = 0, 1

            if self.ID_SELF == 0:
                self.len_1, self.len_2 = int(len_1), int(len_1)
                self.n_int_1 = ((n + 1)*self.len_1 - 1)*self.ny
                self.n_int_2 = ((n + 1)*self.len_2 - 1)*self.ny
                self.A1, self.M1, self.A1g, self.Ag1, self.Agg1, self.M1g, self.Mg1, self.Mgg1 = self.compute_matrices(
                    len_1*(n+1) - 1, n, self.alpha_1, self.lambda_1, 'right', neumann=False)
                self.A2, self.M2, self.A2g, self.Ag2, self.Agg2, self.M2g, self.Mg2, self.Mgg2, self.Neumann_A, self.Neumann_M = self.compute_matrices(
                    len_1*(n+1) - 1, n, self.alpha_1, self.lambda_1, 'right', neumann=True)
            else:
                self.len_1, self.len_2 = int(len_2), int(len_2)
                self.n_int_1 = ((self.n + 1)*self.len_1 - 1)*self.ny
                self.n_int_2 = ((self.n + 1)*self.len_2 - 1)*self.ny
                self.A1, self.M1, self.A1g, self.Ag1, self.Agg1, self.M1g, self.Mg1, self.Mgg1 = self.compute_matrices(
                    len_2*(n+1) - 1, n, self.alpha_2, self.lambda_2, 'left', neumann=False)
                self.A2, self.M2, self.A2g, self.Ag2, self.Agg2, self.M2g, self.Mg2, self.Mgg2, self.Neumann_A, self.Neumann_M = self.compute_matrices(
                    len_2*(n+1) - 1, n, self.alpha_2, self.lambda_2, 'left', neumann=True)
        elif self.WR_type is None:  # testing for theta opt
            pass
        else:
            raise KeyError('invalid WR type')

        if self.WR_type == 'MONOLITHIC':
            self.A, self.M = self.get_monolithic_matrices()

    def get_flux(self, dt, unew, uold, ug_new, ug_old):
        dtinv = 1/dt
        return self.Mg1.dot((unew - uold)*dtinv) + self.Ag1.dot(unew) + self.Mgg1.dot((ug_new - ug_old)*dtinv) + self.Agg1.dot(ug_new)

    # linear interpolation as used
    def interpolation(self, t, data):
        return interp1d(t, data, kind='linear', axis=0, fill_value='extrapolate')

    def norm_interface(self, vec):
        return np.linalg.norm(vec, 2)*self.dx**((self.dim - 1)/2)

    def norm_inner(self, *args):
        if len(args) == 2 and args[1] == 'D':  # inner for a Dirichlet problem
            # Dirichlet matrix are always A1, M1 here, self.len_1 similarly always corresponds to Dirichlet problem
            u1 = args[0]
            return np.sqrt(self.dx**self.dim*self.M1.dot(u1).dot(u1)/self.alpha_1/self.len_1)
        # inner for Neumann problem, (u2, ug) as input
        elif len(args) == 2 and args[1] == 'N':
            # Neumann problem always A2, M2, self.len_2 similarly always corresponds to Neumann problem
            u2, ug = args[0][:-self.ny], args[0][-self.ny:]
            M_dot_u2 = (self.M2.dot(u2) + self.M2g.dot(ug))/self.alpha_2
            M_dot_ug = (self.Mg2.dot(u2) + self.Mgg2.dot(ug))/self.alpha_2
            return np.sqrt(self.dx**self.dim*(M_dot_u2.dot(u2) + M_dot_ug.dot(ug))/self.len_2)
        elif len(args) == 3:  # inner for whole domain, (u1, u2, ug) as input
            if self.WR_type == 'NNWR':
                raise ValueError(
                    'cannot do full discrete norm evaluation using NNWR')
            u1, u2, ug = args[0], args[1], args[2]
            M_dot_u1 = (self.M1.dot(u1) + self.M1g.dot(ug))/self.alpha_1
            M_dot_u2 = (self.M2.dot(u2) + self.M2g.dot(ug))/self.alpha_2
            M_dot_ug = (self.Mg1.dot(u1) + self.Mgg1.dot(ug))/self.alpha_1 + \
                (self.Mg2.dot(u2) + self.Mgg2.dot(ug))/self.alpha_2
            return np.sqrt(self.dx**self.dim*(M_dot_u1.dot(u1) + M_dot_u2.dot(u2) + M_dot_ug.dot(ug))/self.len_total)


    from relaxation import w_i, S_i, DNWR_theta_opt, DNWR_theta_opt_TA, NNWR_theta_opt, NNWR_theta_opt_TA
    from dt_control import get_dt0, get_new_dt_PI, get_new_dt_deadbeat
    from heatCoupling import  solve_dirichlet_SDIRK2, solve_neumann_SDIRK2, runParticipant, runRelaxation

    ##########################################################
    # MONOLITHIC SOLVERS
    ##########################################################
    # IE
    def Monolithic_IE(self, tf, N, init_cond):
        dt = tf/N
        uold = np.hstack(self.get_initial_values(init_cond))
        unew = np.copy(uold)
        for i in range(N):
            uold = unew
            unew = self.linear_solver(self.M + dt*self.A, self.M.dot(uold))
        # slicing to get solutions for the suitable domains/interface
        u1 = unew[:self.n_int_1]
        u2 = unew[self.n_int_1:self.n_int_1 + self.n_int_2]
        ug = unew[-self.ny:]
        flux = self.get_flux(dt, u1, uold[:self.n_int_1], ug, uold[-self.ny:])
        return u1, u2, ug, flux

    # SDIRK2
    def Monolithic_SDIRK2(self, tf, N, init_cond):
        dt = tf/N
        uold = np.hstack(self.get_initial_values(init_cond))
        unew = np.copy(uold)
        for i in range(N):
            uold = unew
            w = self.linear_solver(self.M + self.a*dt*self.A, self.M.dot(uold))
            unew = self.linear_solver(
                self.M + self.a*dt*self.A, self.M.dot(uold) - dt*(1-self.a)*self.A.dot(w))
        # slicing to get solutions for the suitable domains/interface
        u1 = unew[:self.n_int_1]
        u2 = unew[self.n_int_1:self.n_int_1 + self.n_int_2]
        ug = unew[-self.ny:]
        flux = self.get_flux(dt, u1, uold[:self.n_int_1], ug, uold[-self.ny:])
        return u1, u2, ug, flux


if __name__ == '__main__':
    from FSI_verification import get_parameters, get_init_cond
    from FSI_verification import verify_mono_time, visual_verification, verify_space_error

    p_base = get_parameters('test')  # basic testing parameters
    init_cond_1d = get_init_cond(1)
    init_cond_2d = get_init_cond(2)
    a, lam = 1., 0.1

    # Verification of time-integration of monolithic solution
    # 1D
    p1 = {'init_cond': init_cond_1d, 'n': 50, 'dim': 1, 'tf': 1,
          'savefig': 'verify/base/', **p_base}
    verify_mono_time(order=1, k=12, **p1)  # IE
    verify_mono_time(order=2, k=12, **p1)  # SDIRK 2
    visual_verification(order=1, **p1)
    # 2D
    p2 = {'init_cond': init_cond_2d, 'n': 32, 'dim': 2, 'tf': 1,
          'savefig': 'verify/base/', **p_base}
    verify_mono_time(order=1, k=10, **p2)  # IE
    verify_mono_time(order=2, k=8, **p2)  # SDIRK 2
    visual_verification(order=1, **p2)
    # Verification of time-integration of monolithic solution

    # Verification of convergence to space error
    from numpy import pi
    p1 = {'init_cond': init_cond_1d, 'dim': 1, 'tf': 1, **p_base}
    def ex_sol(x, t): return np.exp(-(pi**2)*t*lam/(4*a))*init_cond_1d(x)
    verify_space_error(n_min=2, k=11, ex_sol=ex_sol,
                       savefig='verify/base/', **p1)

    p2 = {'init_cond': init_cond_2d, 'dim': 2, 'tf': 1, **p_base}

    def ex_sol(x, y, t): return np.exp(-5*(pi**2)
                                       * t*lam/(4*a))*init_cond_2d(x, y)
    verify_space_error(n_min=2, k=7, ex_sol=ex_sol,
                       savefig='verify/base/', **p2)

    pp = {'init_cond': get_init_cond(
        2, num=1), 'dim': 2, 'tf': 10000, **get_parameters('air_water')}
    visual_verification(order=2, n=32, **pp)
    pp = {'init_cond': get_init_cond(
        2, num=1), 'dim': 2, 'tf': 10000, **get_parameters('air_steel')}
    visual_verification(order=2, n=32, **pp)
    pp = {'init_cond': get_init_cond(
        2, num=1), 'dim': 2, 'tf': 10000, **get_parameters('water_steel')}
    visual_verification(order=2, n=32, **pp)
