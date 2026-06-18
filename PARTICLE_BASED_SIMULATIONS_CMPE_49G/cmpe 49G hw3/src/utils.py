"""
Utility functions for molecular diffusion simulations.
"""
import numpy as np
from scipy.special import erfc


def compute_distance_to_sphere(position, sphere_center, sphere_radius):
    """
    Compute distance from a point to the surface of a sphere.
    
    Parameters:
    -----------
    position : array-like (3,)
        Point coordinates [x, y, z]
    sphere_center : array-like (3,)
        Center of the sphere [x, y, z]
    sphere_radius : float
        Radius of the sphere
        
    Returns:
    --------
    distance : float
        Minimum distance to sphere surface (negative if inside sphere)
    """
    center_dist = np.linalg.norm(position - sphere_center)
    return center_dist - sphere_radius


def is_inside_sphere(position, sphere_center, sphere_radius):
    """Check if a point is inside a sphere."""
    return np.linalg.norm(position - sphere_center) < sphere_radius


def reflect_point_across_line(point, line_x_int, line_y_int):
    """
    Reflect a point across a line in 2D.
    
    The line is defined by the equation: y = mx + b
    where x_intercept = -b/m and y_intercept = b
    
    Parameters:
    -----------
    point : array-like (2,)
        Point to reflect [x, y]
    line_x_int : float
        X-intercept of the line
    line_y_int : float
        Y-intercept of the line
        
    Returns:
    --------
    reflected_point : ndarray (2,)
        Reflected point [x, y]
    """
    # Line equation: y = mx + b
    # From intercepts: y_int = b, x_int = -b/m
    # So m = -b / x_int = -y_int / x_int
    b = line_y_int
    m = -b / line_x_int  # slope
    
    # Line in form: mx - y + b = 0
    # Reflection formula for point (x0, y0) across line ax + by + c = 0:
    # x' = x0 - 2a(ax0 + by0 + c)/(a^2 + b^2)
    # y' = y0 - 2b(ax0 + by0 + c)/(a^2 + b^2)
    
    # Our line: mx - y + b = 0, so a=m, b=-1, c=b
    a = m
    b_coeff = -1.0
    c = b
    
    x0, y0 = point[0], point[1]
    denom = a**2 + b_coeff**2
    numerator = a * x0 + b_coeff * y0 + c
    
    x_reflected = x0 - 2 * a * numerator / denom
    y_reflected = y0 - 2 * b_coeff * numerator / denom
    
    return np.array([x_reflected, y_reflected])


def distance_to_line_2d(point, line_x_int, line_y_int):
    """
    Compute signed distance from a point to a 2D line.
    
    Parameters:
    -----------
    point : array-like (2,)
        Point [x, y]
    line_x_int : float
        X-intercept of the line
    line_y_int : float
        Y-intercept of the line
        
    Returns:
    --------
    distance : float
        Signed distance (positive/negative indicates side)
    """
    b = line_y_int
    m = -b / line_x_int
    
    # Line: mx - y + b = 0
    a = m
    b_coeff = -1.0
    c = b
    
    x0, y0 = point[0], point[1]
    distance = (a * x0 + b_coeff * y0 + c) / np.sqrt(a**2 + b_coeff**2)
    
    return distance


def is_inside_circle_2d(position, circle_center, circle_radius):
    """Check if a 2D point is inside a circle."""
    return np.linalg.norm(position[:2] - circle_center[:2]) < circle_radius
