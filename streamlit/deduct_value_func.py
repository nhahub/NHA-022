import numpy as np

def get_deduct_value(crack_type: str, density: float) -> float:
    """
    Returns the deduct value for a given crack type and density (medium severity only).
    
    Parameters:
    - crack_type (str): One of 'Alligator Crack', 'Potholes', 'Longitudinal Crack', 'Transverse Crack'
    - density (float): Distress density as a percentage (0-100)
    
    Returns:
    - float: Deduct value (0-100)
    """
    
    # Define logistic curve parameters for each crack type (medium severity)
    crack_curves = {
        'Alligator Crack':      {'Dmax': 65, 'k': 0.20, 'x0': 25},
        'Potholes':             {'Dmax': 70, 'k': 0.25, 'x0': 20},
        'Longitudinal Crack':   {'Dmax': 55, 'k': 0.18, 'x0': 30},
        'Transverse Crack':     {'Dmax': 50, 'k': 0.16, 'x0': 30},
    }
    
    if crack_type not in crack_curves:
        raise ValueError(f"Unsupported crack type: {crack_type}")
    
    params = crack_curves[crack_type]
    Dmax, k, x0 = params['Dmax'], params['k'], params['x0']
    
    # Cap density between 0 and 100
    density = max(0, min(100, density))
    
    # Logistic function
    deduct_value = Dmax / (1 + np.exp(-k * (density - x0)))
    return round(deduct_value, 2)