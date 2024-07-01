# IMPORTS 
import math
import plotly.express as px 
import plotly.graph_objects as go 
from shapely import (Point, LineString, Polygon, LinearRing, MultiPoint, MultiLineString, MultiPolygon, GeometryCollection)


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
    print(f'r1={r1}')
    print(f'r2={r2}')

    # Deep Beam Check 
    deep_beam_check = False 
    ln = l
    if ln/h < 4: 
        deep_beam_check = True 
    
    if deep_beam_check == False: 
        print('Based on given geometry, this is not considered a deep beam per ACI 318-14 9.9.1.1')

    # Initialize Depth to Node Centroids 
    d = 50

    # Determine Maximum Shear Capacity of Cross Section in accordance with ACI 318-14 Eq. 9.9.2.1 
    Phi_Vn_Max = (.75*10*math.sqrt(fc)*b*d)/1000 # kips
    
    if Phi_Vn_Max <= max(v1,v2): 
        print("Beam exceeds maximum shear strength per ACI 318-14 Eq. 9.9.2.1")


    # Calculate Strut/Tie Lengths
    
    L_ac = math.sqrt((a*12)**2 + d**2)
    L_bc = math.sqrt((b1*12)**2 + d**2)
    L_ab = (a*12)+(b1*12)

    
    # Calculate Force in Struts 
    F_ac = (r1*L_ac)/d
    F_bc = (r2*L_bc)/d

    F_ab = r1*((a*12)/d) # Tie Force 

    # Check angle between diagonal struts and horizontal tie 

    strut_1_alpha = math.atan(d/(a*12))
    strut_2_alpha = math.atan(d/(b1*12))

    if math.degrees(strut_1_alpha) < 25: 
        print("NG alpha")
    elif math.degrees(strut_2_alpha) < 25: 
        print("NG alpha")
    
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

    fce_node_c = .85*beta_ccc*fc   #Node at transfer point load
    fce_node_a = .85*beta_cct*fc   # Support A node 
    fce_node_b = .85*beta_cct

    fce_a = min(fce_a,fce_node_a,fce_ac)
    fce_b = min(fce_b,fce_node_b,fce_bc)
    fce_c = min(fce_c,fce_node_c,fce_bc, fce_ac)

    #### Strength and Truss Geometry Checks for STM Nodal Zones & Determine Node Geometry
    # Node C Geometry 
    l_horz_c = (Pu*1000)/(.75*fce_c*b)
    l_dia_c_1 = l_horz_c*(F_ac/Pu)
    l_dia_c_2 = l_horz_c*(F_bc/Pu)
    
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
    l_vert_b = (F_ab*1000)/(.75*fce_b*b)
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
    
    # Plot Shear and Moment Diagrams 

    # Shear Diagram 
    x = [0,0, a, a, l,l]
    y = [0, r1, r1, r1-Pu, -r2, 0]
    shear_fig = go.Figure(data=go.Scatter(x=x, y=y, mode = "lines+markers", line = dict(color='red')))
    shear_fig.update_layout(title = 'Shear Diagram',
                            xaxis_title = 'Position - x',
                            yaxis_title = 'Shear - Vu'
                            )

    
    
    # Moment Diagram
    x = [0,a,l]
    y = [0, (-Pu*a*b)/l, 0]
    moment_fig = go.Figure(data=go.Scatter(x=x, y=y, mode = "lines+markers", line = dict(color='blue')))
    moment_fig.update_layout(title = 'Moment Diagram',
                            xaxis_title = 'Position - x',
                            yaxis_title = 'Moment - Mu'
                            )

    # Shapely Beam Model 


    beam_poly = Polygon([(0,0), (0,h), (l,h),(l,0)])
    

    # Provide plots/graphics of node geometry 
    
    # Tie Reinforcement 
    A_s_req = F_ab/(.75*fy)

    tie_area = ((tie_size/8)**2)*math.pi/4

    num_tie = math.ceil(A_s_req/tie_area) 

    A_s = num_tie*tie_area

    results_dict = {'Phi-Vn': phi_Vn, 'Number of ties':num_tie, 'Beam Model': beam_poly, "Shear Diagram": shear_fig, 'Moment Diagram': moment_fig}

    return results_dict