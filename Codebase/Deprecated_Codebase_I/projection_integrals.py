import numpy as np 
import scipy as sp 
import scipy.special as sp_spcl
import scipy.optimize as sp_opt
import sympy as sy
import matplotlib.pyplot as plt

from Robustness.exception import *
import Robustness.validation as valid
import misc_functions as misc


def line_integral_boundaries(view_line_point,cloud_equation,box_width,
                             view_line_deltas=(1,0,0),n_guesses=100):
    """
    This function determines the points that intersect the sphere, starting
    with it entering and exit. It returns the ranges of points that would
    yield line integral boundaries that integrate within the cloud volume.

    By default, the cloud equation should be a function such that it returns a
    float, f(x,y,z), based on implicit shape making: f(x,y,z) = 0. If not, it
    should be at least a string that contains the python syntax expression of
    the shape for f(x,y,z) = 0, i.e., left-hand side of the equation only.
    """

    # Type check.
    view_line_point = valid.validate_float_array(view_line_point,shape=(3,))
    # Check for both cases.
    try:
        cloud_function = valid.validate_function_call(cloud_equation,   
                                                      n_parameters=3)
    except Exception:
        # Warn the user that sympy parsing is going to be used.
        # Try to use a sympy parsing. Assume a normal cartesian implicit 
        # surface.
        variables = ('x','y','z')
        cloud_function = misc.user_equation_parse(cloud_equation,variables)
    box_width = valid.validate_float_value(box_width,greater_than=0)

    # Define the sightline parametric equations.
    def x_param(t):
        return view_line_deltas[0] * t + view_line_point[0]
    def y_param(t):
        return view_line_deltas[1] * t + view_line_point[1]
    def z_param(t):
        return view_line_deltas[2] * t + view_line_point[2]

    # Assume that the user's function accepts x,y,z in that order.
    def parameterized_cloud_equation(t):
        return cloud_function(x_param(t), y_param(t),z_param(t))

    # Find all of the roots of the parameterized function.
    initial_guesses = np.linspace(-box_width,box_width,n_guesses)
    eq_roots = sp_opt.fsolve(parameterized_cloud_equation,initial_guesses,
                             xtol=1e-10)
    sort_eq_roots = np.sort(eq_roots)

    # Have only unique roots.
    unique_index = (np.abs(sort_eq_roots[1:] - sort_eq_roots[:-1])) > 1e-8
    neg_bound_roots = sort_eq_roots[:-1][unique_index]
    pos_bound_roots = sort_eq_roots[1:][unique_index]

    # There always exists an odd number of regions. The surface is closed and 
    # has an even number of intersections by the sightline that passes in and 
    # out of the surface as per topology. By default, the first and last groups 
    # will not be within the cloud by the closed nature of the cloud. Assume 
    # that the light goes from -x -> +x such that the yz plane is normal when 
    # 'seen', thus the observer is near +x axis head. 
    lower_bounds = neg_bound_roots[0::2]
    upper_bounds = pos_bound_roots[0::2]

    return lower_bounds,upper_bounds


def cloud_line_integral(field_function,cloud_equation,view_line_point, 
                        box_width,
                        view_line_deltas=(1,0,0),n_guesses=100):
    """
    This function computes the total summation of the line integrals given
    a field function that a single sightline passes through, given the 
    boundary that only the section of the line within a cloud would be 
    computed as it is the upper and lower bounds for the integral(s).
    """
    # Type check
    field_function = valid.validate_function_call(field_function,
                                                  n_parameters=3)
    cloud_equation = valid.validate_function_call(cloud_equation,
                                                  n_parameters=3)
    view_line_point = valid.validate_float_array(view_line_point,shape=(3,))
    box_width = valid.validate_float_value(box_width,greater_than=0)
    view_line_deltas = valid.validate_tuple(view_line_deltas,length=3)
    n_guesses = valid.validate_int_value(n_guesses,greater_than=0)


    # Integrating function. Parameterize the field function to integrate over
    # the curve given by the sightline.
        # Define the sightline parametric equations.
    def x_param(t):
        return view_line_deltas[0] * t + view_line_point[0]
    def y_param(t):
        return view_line_deltas[1] * t + view_line_point[1]
    def z_param(t):
        return view_line_deltas[2] * t + view_line_point[2]

    # Assume that the user's function accepts x,y,z in that order.
    def parameterized_field_equation(t):
        return field_function(x_param(t), y_param(t),z_param(t))

    # Determine the lower and upper bounds of the parameterized functional 
    # integrations.
    lower_bounds,upper_bounds = \
        line_integral_boundaries(view_line_point,cloud_equation,box_width,
                                 view_line_deltas,n_guesses)


    # The total integrated number.
    integrated_value = 0
    error = [] # Error array
    for lowerdex,upperdex in zip(lower_bounds,upper_bounds):
        integration = sp.integrate.quad(parameterized_field_equation,
                                        lowerdex,upperdex)
        integrated_value += integration[0]
        error.append(integration[1])

    # Errors add in quadrature.
    error = np.sqrt(np.dot(error,error))
    
    return integrated_value,error


