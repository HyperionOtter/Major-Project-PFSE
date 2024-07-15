# IMPORTS 
import math
import plotly.express as px 
import plotly.graph_objects as go 
from shapely import (Point, LineString, Polygon, LinearRing, MultiPoint, MultiLineString, MultiPolygon, GeometryCollection)
from beam_analysis import beam_load_analysis
import numpy as np



    
def deep_transfer_calc(P_DL:float, P_LL:float, l:float, a:float, h:float, b:float, fc:float, fy=60, tie_size =8,
                       stirrup_size = 5, skin_size=5, stirrup_legs = 2, col1=24.0, col2=24.0):
    '''
    Calculates capacity of simply supported transfer beam with a single point load 
    in accordance with ACI 318-14 Chapter 23 using the strut and tie method for 
    deep beam analysis

    P_DL: Unfactored Dead Point Load (kip)
    P_LL: Unfactored Live Point Load (kip)
    a: location of point load on beam (ft)
    h: Beam Height (in)
    b: Beam Width (in)
    fc: Concrete compressive strength (psi)
    l: Beam Length (ft) length is column center to column center 
    col1: Column 1 Width (in) - 1 is assumed to be left
    col2: Column 2 Width (in) - 1 is assumed to be left
    tie_size: Tension/tie reinforcement bar size 
    '''

    #_________________________________Calculate Forces  ___________________________________#
    # Calculate Contribution of Beam Self Weight and add to point load
    sw = 150*(h/12)*(b/12)*(l+col1/24 + col2/24)/1000  # Calculates self weight of beam
    

    P_DL_total = P_DL + sw # Adds self weight to dead load reaction 

    # Determine Max Factored Point Load on Beam
    Pu = max([1.2*P_DL_total+1.6*P_LL,1.4*P_DL_total])


    # Determine Reactions on Beam 
    b1 = l-a
    r1 = (Pu*b1)/l
    r2 = (Pu*a)/l
    v1 = r1 
    v2 = r2 
    print(f"r1={r1}")
    print(f"r2={r2}")

    #____________________________Strut and Tie Analysis ______________________________#

    # Initialize Depth to Node Centroids 
    cover = 5
    d = h-cover
    

    # Calculate Strut/Tie Lengths
    L_ac = math.sqrt((a*12)**2 + (d)**2)
    print(f"L_ac = {L_ac}")
    L_bc = math.sqrt((b1*12)**2 + d**2)
    L_ab = (a*12)+(b1*12)

    
    # Calculate Force in Struts 
    F_ac = (r1*L_ac)/(d)
    F_bc = (r2*L_bc)/d
    print(f"Fac = {F_ac}")

    F_ab = r1*((a*12)/(d)) # Tie Force 
    print(f"tie fohhrce = {F_ab}")

    # Check angle between diagonal struts and horizontal tie 
    strut_1_alpha = math.atan(d/(a*12))
    print(F'alpha 1 = {strut_1_alpha}')
    strut_2_alpha = math.atan(d/(b1*12))
    
    # Check/Provide Vertical and Horizontal Reinforcement to Resist Splitting of STM Diagonal Struts 
    s_req = round(min(d/5, 12)) # Minimum spacing of skin reinforcement

        # Strut 1 

    
        # Strut 2 

    
    # Determine Effective Concrete Strength of Struts 
    beta_s = .75 # Coefficient for bottle shaped struts as per ACI 23.5.1 

    fce_ac = .85*beta_s*fc 
    fce_bc = .85*beta_s*fc
    
    fce_a = .85*1*fc  # Support struts, assumed to have uniform cross sectional area 
    fce_b = fce_a
    fce_c = fce_a

    # Determine Effective Concrete Strength of Nodes 
    beta_ccc = 1.0 # Coefficient for CCC node
    beta_cct = .80  # Coefficient for CCT node

    fce_node_c = .85*beta_ccc*fc   # Node at transfer point load
    fce_node_a = .85*beta_cct*fc   # Support A node 
    fce_node_b = .85*beta_cct*fc

    fce_a = min(fce_a,fce_node_a,fce_ac)
    fce_b = min(fce_b,fce_node_b,fce_bc)
    fce_c = min(fce_c,fce_node_c,fce_bc, fce_ac)
    

    #### Strength and Truss Geometry Checks for STM Nodal Zones & Determine Node Geometry
    # Node C Geometry 
    l_horz_c = (Pu*1000)/(.75*fce_c*b)
    print(f'Pu = {Pu}')
    print(f'l_horz_c = {l_horz_c}')
    l_dia_c_1 = l_horz_c*(F_ac/Pu)
    print(f'l_dia_c1 = {l_dia_c_1}')
    l_dia_c_2 = l_horz_c*(F_bc/Pu)
    l_vert_c_1 = math.sqrt(l_dia_c_1**2 - (l_horz_c/2))
    
    # Calculate centroid of node c 
    s = (l_dia_c_1+l_dia_c_2+l_horz_c)/2
    A = math.sqrt(s*(s-l_dia_c_1)*(s-l_dia_c_2)*(s-l_horz_c))
    node_c_height = 2*A/(l_horz_c)
    node_c_centroid = node_c_height/3

    # Node A Geometry
    l_vert_a = (F_ab*1000)/(.75*fce_a*b)
    l_horz_a = (r1*1000)/(.75*fce_a*b)
    l_dia_a = math.sqrt(l_vert_a**2 + l_horz_a**2)
    

    # Node B Geometry
    print(f'fce_b = {fce_b}')
    l_vert_b = (F_ab*1000)/(.75*fce_b*b)
    print(f' l_vert_b = {l_vert_b}')
    l_horz_b = (r2*1000)/(.75*fce_b*b)
    l_dia_b = math.sqrt(l_vert_b**2 + l_horz_b**2)

    # Node A Capacity 
    a_nz_a = l_dia_a*b
    fnn_a = a_nz_a*fce_a
    vn_a = fnn_a*math.sin(strut_1_alpha)

    # Node B Capacity 
    a_nz_b = l_dia_b*b
    fnn_b = a_nz_b*fce_b
    vn_b = fnn_b*math.sin(strut_2_alpha)

    # Node C Capacity 
    a_nz_c = min(l_dia_c_1, l_dia_c_2)*b
    fnn_c = a_nz_c*fce_c
    vn_c = fnn_c*math.sin(min(strut_1_alpha,strut_2_alpha))
    

    phi_Vn = .75*min(vn_a, vn_b,vn_c)
    
    #____________________________Plot of Strut and Tie Model ______________________________#

    beam_poly = Polygon([(-col1/24,0), (-col1/24,h), (l+col2/24,h),(l+col2/24,0)])

    x, y = beam_poly.exterior.xy
    x = list(x)  # Convert to list
    y = list(y)  # Convert to list
    fig = go.Figure(
            data=go.Scatter(
                x=x, 
                y=y, 
                mode='lines', 
                fill='toself', 
                line=dict(color='blue'),  # Customize line color
                fillcolor='rgba(0, 0, 255, 0.1)'  # Customize fill color with transparency
            )

        
        )

    fig.add_trace(go.Scatter(x=[a-.2, a, a], y =[h+4, h+1, h+15], mode = 'lines',
                                 line = dict(color='black')))
        
    fig.add_trace(go.Scatter(x=[a,a+.2], y =[h+1, h+4], mode = 'lines',
                                 line = dict(color='black')))
        
    fig.add_trace(go.Scatter(x=[0, .4, -.4, 0 ], y =[0, -5, -5, 0], mode = 'lines',
                                 line = dict(color='black')))
    
    
        
    radius = 3
    center_x = l
    center_y = -3

    # Create points for roller support
    theta = np.linspace(0, 2 * np.pi, 100)
    x = center_x + radius/12 * np.cos(theta)
    y = center_y + radius * np.sin(theta)


    # Add Lines for struts and tie 
    # Tie 
    fig.add_trace(go.Scatter(x=[0, l], y =[h-d, h-d], mode = 'lines',
                                 line = dict(color='black', dash = 'dash')))
    
    # Strut AC 
    fig.add_trace(go.Scatter(x=[0, a], y =[h-d, h-cover], mode = 'lines',
                                 line = dict(color='black')))   
    
    # Strut BC 
    fig.add_trace(go.Scatter(x=[a, l], y =[h-cover, h-d], mode = 'lines',
                                 line = dict(color='black')))   

    # Add figures for nodes 
    # Node C 
    fig.add_trace(go.Scatter(x=[a-(l_horz_c/2)/12, a+(l_horz_c/2)/12], y =[h-cover, h-cover], mode = 'lines',
                                 line = dict(color='black')))  
    fig.add_trace(go.Scatter(x=[a-(l_horz_c/2)/12, a], y =[h-cover, h-cover-l_vert_c_1/12], mode = 'lines',
                                 line = dict(color='black')))
    fig.add_trace(go.Scatter(x=[a+(l_horz_c/2)/12, a], y =[h-cover, h-cover-l_vert_c_1/12], mode = 'lines',
                                 line = dict(color='black')))
    
    # Node A
    fig.add_trace(go.Scatter(x=[-l_horz_a/24, l_horz_a/24], y =[h-d, h-d], mode = 'lines',
                                 line = dict(color='black')))  
    fig.add_trace(go.Scatter(x=[-l_horz_a/24, -l_horz_a/24], y =[h-d, h-d+l_vert_a/12], mode = 'lines',
                                 line = dict(color='black')))  
    fig.add_trace(go.Scatter(x=[l_horz_a/24, -l_horz_a/24], y =[h-d, h-d+l_vert_a/12], mode = 'lines',
                                 line = dict(color='black')))  
    
    # Node B 


    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', line=dict(color='black')))

    annotations = [
    dict(x=.5, y=cover-3 , text="NODE A", showarrow=True, arrowhead=2, ax=-3, ay=-5), 
    dict(x=l-.5, y=cover - 3, text="NODE B", showarrow=True, arrowhead=2, ax=-3, ay=-5),
    dict(x=a-.6, y=h+2, text="NODE C", showarrow=True, arrowhead=2, ax=-3, ay=-5), 
    dict(x=a/3.8, y=7, text=f"{round(math.degrees(strut_1_alpha),1)}°", showarrow=True, arrowhead=2, ax=-3, ay=-5),
    dict(x=l-1.4, y=7, text=f"{round(math.degrees(strut_2_alpha),1)}°", showarrow=True, arrowhead=2, ax=-3, ay=-5)]
                    


    fig.update_layout(
            title="Strut and Tie Model",
            xaxis_title="Beam Span (ft)",
            yaxis_title="Beam Height (in)",
            showlegend=False,
            width = 800, 
            height = 800,
            xaxis=dict(
                range=[-col1/12, l+col2/12],  # Specify the x-axis range
                scaleanchor="y",
                scaleratio=12,
            ),
            yaxis=dict(
                visible = False,
                range = [0, h+2],
                scaleanchor="x",
                scaleratio=1,
            ),
            annotations=annotations
        )

    # Standlone Figure for Node A
    node_a_fig = go.Figure()
 
    node_a_fig.add_trace(go.Scatter(x=[0, l_horz_a], y =[0, 0], mode = 'lines',
                                 line = dict(color='black')))  
    node_a_fig.add_trace(go.Scatter(x=[0, 0], y =[0, l_vert_a], mode = 'lines',
                                 line = dict(color='black')))  
    node_a_fig.add_trace(go.Scatter(x=[l_horz_a, 0], y =[0, l_vert_a], mode = 'lines',
                                 line = dict(color='black')))  
    
    node_a_fig.update_layout(
            title="Node A Geometry",
            xaxis_title="in",
            yaxis_title="",
            showlegend=False,
            xaxis=dict(
                  # Specify the x-axis range
                scaleanchor="y",
                scaleratio=1,
            ),
            yaxis=dict(
                
                scaleanchor="x",
                scaleratio=1,
            )
        )
    
    # Standlone Figure for Node B
    node_b_fig = go.Figure()
 
    node_b_fig.add_trace(go.Scatter(x=[0, l_horz_b], y =[0, 0], mode = 'lines',
                                 line = dict(color='black')))  
    node_b_fig.add_trace(go.Scatter(x=[l_horz_b, l_horz_b], y =[0, l_vert_b], mode = 'lines',
                                 line = dict(color='black')))  
    node_b_fig.add_trace(go.Scatter(x=[l_horz_b, 0], y =[l_vert_b, 0], mode = 'lines',
                                 line = dict(color='black')))  
    print(l_horz_b)
    
    node_b_fig.update_layout(
            title="Node B Geometry",
            xaxis_title="in",
            yaxis_title="",
            showlegend=False,
            xaxis=dict(
                  # Specify the x-axis range
                scaleanchor="y",
                scaleratio=1,
            ),
            yaxis=dict(
                
                scaleanchor="x",
                scaleratio=1,
            )
        )
    
    # Standlone Figure for Node C
    node_c_fig = go.Figure()

    node_c_fig.add_trace(go.Scatter(x=[0, l_horz_c], y =[0, 0], mode = 'lines',
                                 line = dict(color='black')))  
    node_c_fig.add_trace(go.Scatter(x=[0, l_horz_c], y =[0, 0], mode = 'lines',
                                 line = dict(color='black')))  
    node_c_fig.add_trace(go.Scatter(x=[0, l_horz_c], y =[0, 0], mode = 'lines',
                                 line = dict(color='black')))  
    
    node_c_fig.update_layout(
            title="Node C Geometry",
            xaxis_title="in",
            yaxis_title="",
            showlegend=False,
            xaxis=dict(
                  # Specify the x-axis range
                scaleanchor="y",
                scaleratio=1,
            ),
            yaxis=dict(
                
                scaleanchor="x",
                scaleratio=1,
            )
        )
    
    
    # l_horz_c = (Pu*1000)/(.75*fce_c*b)
    # print(f'Pu = {Pu}')
    # print(f'l_horz_c = {l_horz_c}')
    # l_dia_c_1 = l_horz_c*(F_ac/Pu)
    # print(f'l_dia_c1 = {l_dia_c_1}')
    # l_dia_c_2 = l_horz_c*(F_bc/Pu)
    # l_vert_c_1 = math.sqrt(l_dia_c_1**2 - (l_horz_c/2))






    
    # Tie Reinforcement 
    A_s_req = F_ab/(.75*fy)

    tie_area = ((tie_size/8)**2)*math.pi/4

    num_tie = math.ceil(A_s_req/tie_area) 

    A_s = num_tie*tie_area

    results_dict = {'Phi-Vn': phi_Vn, 'Number of ties':num_tie, 'Strut and Tie Model': fig, 
                    'alpha_1':strut_1_alpha, 'alpha_2':strut_2_alpha, 'Node A Figure': node_a_fig, 'Node B Figure': node_b_fig,
                    'Node C Figure': node_c_fig}

    return results_dict