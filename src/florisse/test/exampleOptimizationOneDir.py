from openmdao.api import Problem, ScipyOptimizer, pyOptSparseDriver
from florisse.OptimizationGroups import OptPowerOneDir

import time
import numpy as np


if __name__ == "__main__":

    # define turbine size
    rotor_diameter = 126.4  # (m)

    # define turbine locations in global reference frame
    nRows = 3       # number of rows and columns in grid
    spacing = 5     # turbine grid spacing in diameters
    points = np.linspace(start=spacing*rotor_diameter, stop=nRows*spacing*rotor_diameter, num=nRows)
    xpoints, ypoints = np.meshgrid(points, points)
    turbineX = np.ndarray.flatten(xpoints)
    turbineY = np.ndarray.flatten(ypoints)

    # initialize input variable arrays
    nTurbs = turbineX.size
    rotorDiameter = np.zeros(nTurbs)
    axialInduction = np.zeros(nTurbs)
    Ct = np.zeros(nTurbs)
    Cp = np.zeros(nTurbs)
    generator_efficiency = np.zeros(nTurbs)
    yaw = np.zeros(nTurbs)

    # define initial values
    for turbI in range(0, nTurbs):
        rotorDiameter[turbI] = rotor_diameter      # m
        axialInduction[turbI] = 1.0/3.0
        Ct[turbI] = 4.0*axialInduction[turbI]*(1.0-axialInduction[turbI])
        Cp[turbI] = 0.7737/0.944 * 4.0 * 1.0/3.0 * np.power((1 - 1.0/3.0), 2)
        generator_efficiency[turbI] = 0.944
        yaw[turbI] = 10.     # deg.

    # Define flow properties
    wind_speed = 8.0        # m/s
    air_density = 1.1716    # kg/m^3
    wind_direction = 240    # deg (N = 0 deg., using direction FROM, as in met-mast data)

    # initialize problem
    prob = Problem(root=OptPowerOneDir(nTurbs, resolution=0))

    # set up optimizer
    prob.driver = pyOptSparseDriver()
    prob.driver.options['optimizer'] = 'SNOPT'

    # set optimizer options
    prob.driver.opt_settings['Verify level'] = 3
    prob.driver.opt_settings['Print file'] = 'SNOPT_print_exampleOptOneDir.out'
    prob.driver.opt_settings['Summary file'] = 'SNOPT_summary_exampleOptOneDir.out'

    # prob.driver.options['tol'] = 1.0E-8
    prob.driver.add_desvar('turbineX', low=np.ones(nTurbs)*min(turbineX), high=np.ones(nTurbs)*max(turbineX))
    prob.driver.add_desvar('turbineY', low=np.ones(nTurbs)*min(turbineY), high=np.ones(nTurbs)*max(turbineY))
    prob.driver.add_desvar('yaw0', low=-30.0, high=30.0)
    prob.driver.add_objective('obj')

    # initialize problem
    prob.setup()

    # assign initial values to design variables
    prob['turbineX'] = turbineX
    prob['turbineY'] = turbineY
    prob['yaw0'] = yaw

    # assign values to constant inputs (not design variables)
    prob['rotorDiameter'] = rotorDiameter
    prob['axialInduction'] = axialInduction
    prob['generator_efficiency'] = generator_efficiency
    prob['wind_speed'] = wind_speed
    prob['air_density'] = air_density
    prob['windDirections'] = np.array([wind_direction])
    prob['Ct_in'] = Ct
    prob['Cp_in'] = Cp
    prob['floris_params:FLORISoriginal'] = True
    prob['floris_params:CPcorrected'] = False
    prob['floris_params:CTcorrected'] = False

    # run the problem
    print 'start FLORIS run'
    tic = time.time()
    prob.run()
    toc = time.time()

    # print the results
    print('FLORIS Opt. calculation took %.03f sec.' % (toc-tic))
    print 'turbine powers (kW): %s' % prob['wt_power0']
    print 'turbine X positions in wind frame (m): %s' % prob['turbineX']
    print 'turbine Y positions in wind frame (m): %s' % prob['turbineY']
    print 'yaw (deg) = ', prob['yaw0']
    print 'effective wind speeds (m/s): %s' % prob['velocitiesTurbines0']
    print 'wind farm power (kW): %s' % prob['power0']

    # data = prob.check_partial_derivatives()

