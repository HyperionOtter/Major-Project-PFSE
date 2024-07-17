# IMPORTS 
import plotly.graph_objects as go 
from shapely import (Point, LineString, Polygon, LinearRing, MultiPoint, MultiLineString, MultiPolygon, GeometryCollection)
import numpy as np


def linearly_decreasing_with_step(x, a, l, r1,  r2, sw_line, Pu):
    """
    Function to plot y values of shear diagram for bernoulli beam case, as selfweight is a line load,
    there will be a linearly decreasing shear with a step down at the point load location 
    
    """
    y = np.piecewise(
         x,
            [x ==0, x < a, (x > a) & (x < l), x>=l],
            [r1, lambda x: r1 -1.2*sw_line*x, lambda x: r1 - Pu -1.2*sw_line*x, -r2]
    )
    return y 



def beam_load_analysis(P_DL:float, P_LL:float, l:float, a:float, h:float, b:float, col1=24.0, col2=24.0): 
    """
    Returns dictionary of Pu, shear and moment diagram figures for both bernoulli and deep beams
    Shear Diagram will differ between deep beam and bernoulli beam, in the case of a deep beam
    the self weight contribution is added to the concentrated force. In the case of the bernoulli
    beam, the self weight will be treated as a typical line load. 

    """

    # Calculate Contribution of Beam Self Weight and add to point load
    sw = 150*(h/12)*(b/12)*(l+col1/24 + col2/24)/1000  # Calculates self weight of beam

    P_DL_total = P_DL + sw # Adds self weight to dead load reaction 

    # Determine Max Factored Point Load on Beam
    Pu = max([1.2*P_DL_total+1.6*P_LL,1.4*P_DL_total])
    Pu_bb = max([1.2*P_DL+1.6*P_LL,1.4*P_DL])

    #____________________________Load Analysis for Deep Beam ______________________________#

    # Determine Reactions on Deep Beam 
    b1 = l-a
    r1 = (Pu*b1)/l
    r2 = (Pu*a)/l
    v1 = r1 
    v2 = r2 
 
    

    # Shear Diagram 
    x = [0,0, a, a, l,l]
    y = [0, r1, r1, r1-Pu, -r2, 0]
    shear_fig_db = go.Figure(data=go.Scatter(x=x, y=y, mode = "lines+markers", line = dict(color='red')))
    shear_fig_db.update_layout(title = 'Shear Diagram',
                            xaxis_title = 'Position - x',
                            yaxis_title = 'Shear - Vu', 
                            width = 575, 
                            height = 500
                            )

    
    # Moment Diagram
    x = [0,a,l]
    y = [0, (-Pu*a*b)/l, 0]
    moment_fig_db = go.Figure(data=go.Scatter(x=x, y=y, mode = "lines+markers", line = dict(color='blue')))
    moment_fig_db.update_layout(title = 'Moment Diagram',
                            xaxis_title = 'Position - x',
                            yaxis_title = 'Moment - Mu (kip-ft)', 
                            width = 575, 
                            height = 500
                            )

    # Shapely Beam Model 
    beam_poly = Polygon([(0,0), (0,h), (l,h),(l,0)])


    #____________________________Load Analysis for Bernoulli Beam ______________________________#



    # Calculate Contribution of Beam Self Weight and add to point load
    sw_line = 150*(h/12)*(b/12)/1000 # Beam Self Weight Line Load 

    # Determine Reactions on Deep Beam 

    r1_bb = (Pu_bb*b1)/l  + 1.2*(sw_line*l/2)
    r2_bb = (Pu_bb*a)/l  + 1.2*(sw_line*l/2)

    x_diagram = np.linspace(0, l)
    y_bb = linearly_decreasing_with_step(x_diagram, a, l, r1_bb,  r2_bb, sw_line, Pu_bb)

    Vu_bb = max(r1, r2)

    # Shear Diagram 
   
    shear_fig_bb = go.Figure(data=go.Scatter(x=x_diagram, y=y_bb, mode = "lines", line = dict(color='red')))
    shear_fig_bb.update_layout(title = 'Shear Diagram',
                            xaxis_title = 'Position - x',
                            yaxis_title = 'Shear - Vu (kip)'
                            )
    
    # Moment Diagram
    Mu_bb = Pu*a*b/(l)  + (sw_line*l**2)/8
    print(f"Mu_bb = {Mu_bb}")
    x = [0,a,l]
    y = [0, (-Pu*a*b)/l, 0]
    moment_fig_bb = go.Figure(data=go.Scatter(x=x, y=y, mode = "lines+markers", line = dict(color='blue')))
    moment_fig_bb.update_layout(title = 'Moment Diagram',
                            xaxis_title = 'Position - x',
                            yaxis_title = 'Moment - Mu'
                            )


    #_____________________________________Deep Beam Check ______________________________________#

    # Check whether it is a bernoulli beam or a deep beam 
    if (l*12)/h <= 4: 
        deep_beam = True 
        load_results = {'Pu': Pu, 'Beam_Poly': beam_poly, 'Deep Beam': deep_beam, 'Shear Diagram': shear_fig_db, 'Moment Diagram': moment_fig_db, 'R1':r1, 'R2': r2}
    else: 
        deep_beam = False 
        load_results = {'Pu': Pu_bb, 'Beam_Poly': beam_poly, 'Deep Beam': deep_beam, 'Shear Diagram': shear_fig_bb, 'Moment Diagram': moment_fig_bb, 'Vu': Vu_bb, 'Mu':Mu_bb}

    return load_results