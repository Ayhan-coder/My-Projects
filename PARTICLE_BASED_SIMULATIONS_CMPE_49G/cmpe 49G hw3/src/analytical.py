"""
Analytical formulations for molecular communication channels.
"""
import numpy as np
from scipy.special import erfc


def channel_response_3d(t, r_rx, d, D, N_tx=1.0):
    """
    Compute analytical cumulative received molecules for 3D diffusion.
    
    Formula: N_Rx(t) = N_Tx * (r_Rx / (r_Rx + d)) * erfc(d / sqrt(4*D*t))
    
    Parameters:
    -----------
    t : float or ndarray
        Time(s) at which to evaluate the channel response
    r_rx : float
        Receiver radius (micrometers)
    d : float
        Distance between emission point and receiver surface (micrometers)
    D : float
        Diffusion coefficient (micrometers^2/second)
    N_tx : float, optional
        Number of transmitted molecules (default: 1.0)
        
    Returns:
    --------
    N_rx : float or ndarray
        Cumulative number of received molecules at time t
    """
    # Avoid division by zero and numerical issues
    t = np.asarray(t)
    result = np.zeros_like(t, dtype=float)
    
    valid_mask = t > 0
    
    if np.any(valid_mask):
        t_valid = t[valid_mask] if t.ndim > 0 else t
        factor = (r_rx / (r_rx + d)) * erfc(d / np.sqrt(4 * D * t_valid))
        
        if t.ndim > 0:
            result[valid_mask] = N_tx * factor
        else:
            result = N_tx * factor
    
    return result


def channel_response_3d_impulse(t, r_rx, d, D):
    """
    Compute the derivative (impulse response) of the 3D channel response.
    
    This gives the instantaneous (non-cumulative) received signal.
    
    Parameters:
    -----------
    t : float or ndarray
        Time(s)
    r_rx : float
        Receiver radius
    d : float
        Distance to receiver surface
    D : float
        Diffusion coefficient
        
    Returns:
    --------
    h : float or ndarray
        Impulse response at time t
    """
    t = np.asarray(t)
    result = np.zeros_like(t, dtype=float)
    
    valid_mask = t > 0
    
    if np.any(valid_mask):
        t_valid = t[valid_mask] if t.ndim > 0 else t
        sqrt_term = np.sqrt(np.pi * D * t_valid)
        exp_term = np.exp(-(d**2) / (4 * D * t_valid))
        factor = (r_rx / (r_rx + d)) * (d / sqrt_term) * exp_term
        
        if t.ndim > 0:
            result[valid_mask] = factor
        else:
            result = factor
    
    return result
