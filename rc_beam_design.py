import math
import plotly.graph_objects as go 
from shapely import Polygon


def rc_beam_design(fc, fy, b, h, Mu, Vu, l, tie_size:int):
    # Constants
    phi_flexure = 0.9
    phi_shear = 0.75
    tie_area = (tie_size**2)*math.pi/4
    
    Mu = Mu
    d = .9*h
    print(f"Mu = {Mu}")
    # Calculate required area of steel (As)
    beta1 = min(0.85, max(0.85 - 0.05 * ((fc - 4000) / 1000), 0.65))
    rho_min = max(3 * math.sqrt(fc) / fy, 200 / fy)
    rho_max = 0.75 * beta1 * (fc / fy) * (60000 / fy)
    
    As_min = rho_min * b * d
    As_max = rho_max * b * d
    
    a = (Mu / (phi_flexure * 0.85 * fc * b))**(1/2)
    As = (Mu / (phi_flexure * fy * (d - a/2)))
    print(f" As = {As}")
    
    # Check if As is within limits
    if As < As_min:
        As = As_min
    elif As > As_max:
        As = As_max
    print(f" As_max = {As_max}")
    
    # Check shear capacity
    lambda_factor = 1.0  # Normal-weight concrete
    Vc = lambda_factor * 2 * (fc**0.5) * b * d / 1000  # Shear capacity of concrete (lb)
    Vn = Vc
    
    if Vu > phi_shear * Vc:
        Vs = (Vu - phi_shear * Vc) / phi_shear
        stirrup_spacing = (phi_shear * 0.75 * fy * b * d) / Vs
    else:
        stirrup_spacing = None  # No stirrups required

    beam_poly = Polygon([(0,0), (0,h), (l,h),(l,0)])
    
    # Reinforcement Plot/Diagram

    x, y = beam_poly.exterior.xy
    x = list(x)  # Convert to list
    y = list(y)  # Convert to list
    reinf_fig = go.Figure(
            data=go.Scatter(
                x=x, 
                y=y, 
                mode='lines', 
                fill='toself', 
                line=dict(color='blue'),  # Customize line color
                fillcolor='rgba(0, 0, 255, 0.1)'  # Customize fill color with transparency
            )

        
        )
    
    return {
        'As': As,
        'Number of ties': math.ceil(As/tie_area), 
        'As_min': As_min,
        'As_max': As_max,
        'Vc': Vc,
        'stirrup_spacing': stirrup_spacing
    }