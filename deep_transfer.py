# IMPORTS 
import plotly.express as px 
import plotly.graph_objects as go
import streamlit as st
from deep_transfer_app import deep_transfer_calc
import numpy as np
from beam_analysis import beam_load_analysis
from rc_beam_design import rc_beam_design
import math

# Streamlit UI 

st.markdown('# RC Transfer Beam Design')
concrete_strengths = [4000, 5000, 6000, 7000]
yield_strengths = [60, 70, 80]
st.sidebar.subheader("Material Properties")
concrete_strength = st.sidebar.selectbox('Concrete Compressive Strength (psi)', options=concrete_strengths)
yield_strength = st.sidebar.selectbox('Reinforcement Yield Strength (ksi)', options=yield_strengths)

st.sidebar.subheader("Transfer Forces")
P_DL_stream = st.sidebar.number_input("Dead Load Transfer Force (kip)")
P_LL_stream = st.sidebar.number_input("Live Load Transfer Force (kip)")

st.sidebar.subheader("Transfer Beam Geometry")
l_stream = st.sidebar.number_input("Beam Length (ft)")
a_stream = st.sidebar.number_input("Transfer Column Location (ft)")
h_stream = st.sidebar.number_input("Beam Depth (in)")
b_stream = st.sidebar.number_input("Width (in)")

st.sidebar.subheader("Column Dimensions")
c1_stream = st.sidebar.number_input("Column 1 Width (in)")
c2_stream = st.sidebar.number_input("Column 2 Width (in)")

st.sidebar.subheader("Beam Reinforcement")
bar_sizes = [4,5,6,7,8,9,10,11,14]
tie_size_stream = st.sidebar.selectbox("Tension Reinforcement Bar Size", options=bar_sizes)
stirrup_sizes = [4,5,6]
stirrup_size_stream = st.sidebar.selectbox("Stirrup Bar Size", options=stirrup_sizes)
leg_list = [2,4,6]
stirrup_legs_stream = st.sidebar.selectbox("Number of Stirrup Legs", options=leg_list)
skin_bar_sizes = [4,5,6,7,8]
skin_bar_size_stream = st.sidebar.selectbox("Skin Bar Size", options=skin_bar_sizes)


# Function to plot beam model from shapely polygon - defined in beam analysis function
def create_plot(polygon, l):
        '''
        Function to create a plotly plot of the conceptual beam model for illustrative purposes, 
        includes beam block, a pin support on the left side of the beam and a roller on the right side, 
        also includes an arrow for the point load. 
        Returns a plotly figure of the beam model 
        
        '''
        x, y = polygon.exterior.xy
        x = list(x)  # Convert to list
        y = list(y)  # Convert to list
        fig = go.Figure(
            data=go.Scatter(
                x=x, 
                y=y, 
                mode='lines', 
                fill='toself', 
                line=dict(color='blue'),  # Customize line color
                fillcolor='rgba(0, 0, 255, 0.3)'  # Customize fill color with transparency
            )

        
        )

        fig.add_trace(go.Scatter(x=[a_stream-.2, a_stream, a_stream], y =[h_stream+4, h_stream+1, h_stream+15], mode = 'lines',
                                 line = dict(color='black')))
        
        fig.add_trace(go.Scatter(x=[a_stream,a_stream+.2], y =[h_stream+1, h_stream+4], mode = 'lines',
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

        # Create the Plotly figure
        fig.add_trace(go.Scatter(x=x, y=y, mode='lines', line=dict(color='black')))


        fig.update_layout(
            title="Beam Model",
            xaxis_title="Beam Span (ft)",
            yaxis_title="Beam Height (in)",
            showlegend=False,
            width = 600,
            height = 500,
            xaxis=dict(
                range=[-1, l+1],  # Specify the x-axis range
                scaleanchor="y",
                scaleratio=12,
            ),
            yaxis=dict(
                visible = False,
                range = [-1, h_stream+1],
                scaleanchor="x",
                scaleratio=1,
            ),
        )
        return fig  
tab1, tab2, tab3 = st.tabs(["Beam Analysis", "Strut and Tie Design", "Bernoulli Beam Design"])



# Run Beam Load Analysis Function to get Load Diagrams and Beam Model 

try: results = beam_load_analysis(P_DL=P_DL_stream, P_LL=P_LL_stream,l=l_stream,a=a_stream,h=h_stream,
                   b=b_stream,col1=c1_stream,col2=c2_stream)
except ZeroDivisionError: 
     st.header('Confirm all inputs are valid')
d = .9*h_stream
Phi_Vn_Max = (.75*10*math.sqrt(concrete_strength)*b_stream*d)/1000 # kips

#_______________________________Plot Analysis Figures __________________________________#

# Plot Beam Conceptual Model 
beam_poly = results['Beam_Poly']
beam_plot = create_plot(polygon = beam_poly, l = l_stream)

# Shear Diagram 
shear_fig = results['Shear Diagram']

#Moment Diagram 
moment_fig = results['Moment Diagram']

with tab1:
     beam_fig = st.plotly_chart(beam_plot)
     shear_diagram = st.plotly_chart(shear_fig)
     moment_diagram = st.plotly_chart(moment_fig)
    
# Deep Beam Check

if results["Deep Beam"] == True: 
    with tab3: 
         st.markdown('Beam is considered a deep beam per ACI 318-14 9.9.1.1 Strut and Tie will be used for analysis/design')
    if max(results['R1'], results['R2'])> Phi_Vn_Max:
         st.markdown("Beam exceeds maximum shear strength per ACI 318-14 Eq. 9.9.2.1")

    try: 

        design_results = deep_transfer_calc(P_DL=P_DL_stream, P_LL=P_LL_stream,l=l_stream,a=a_stream,h=h_stream,
                   b=b_stream,fc=concrete_strength,fy=yield_strength,tie_size=tie_size_stream,
                   stirrup_size=stirrup_size_stream, skin_size=skin_bar_size_stream,
                   stirrup_legs=stirrup_legs_stream,col1=c1_stream,col2=c2_stream)
    except ZeroDivisionError: 
         st.subheader('It looks like there is a zero division error, confirm all inputs are filled in')
    
    st_model = design_results["Strut and Tie Model"]

    # Alpha Angles 
    alpha_1 = design_results["alpha_1"]
    alpha_2 = design_results["alpha_2"]

    with tab2: 
        st.markdown('Beam is considered a deep beam per ACI 318-14 9.9.1.1 Strut and Tie will be used for analysis/design')
        st_fig = st.plotly_chart(st_model)

        # Plot Node Figures 
        node_a_fig = st.plotly_chart(design_results['Node A Figure'])
        node_b_fig = st.plotly_chart(design_results['Node B Figure'])
        node_c_fig = st.plotly_chart(design_results['Node C Figure'])
        test_fig = st.plotly_chart(design_results['Test Fig'])

        # Plot Reinforcement Diagram 
        reinf_fig = design_results["Reinforcement Diagram"]
        reinf_plot = st.plotly_chart(reinf_fig)

        # Results Outputs 
        # st.markdown('**Number of Ties/Tension Bars Required:**')
        # st.markdown(design_results['Number of ties'])

        #  Alpha Angle Check 
        if math.degrees(alpha_1)< 25: 
            st.markdown('Alpha 1 is less than 25 degrees, as per ACI 318-14. The angle between the axes of any strut and any tie entering a single node shall be at least 25 degrees')
            st.markdown('Revise Beam Geometry to Correct Alpha 1')
        else: 
            st.markdown('Alpha 1 is greater than 25 degrees, as per ACI 318-14.')
            st.markdown('OK')
        if math.degrees(alpha_2)< 25: 
            st.markdown('Alpha 2 is less than 25 degrees, as per ACI 318-14. The angle between the axes of any strut and any tie entering a single node shall be at least 25 degrees')
            st.markdown('Revise Beam Geometry to Correct Alpha 2')
        else: 
            st.markdown('Alpha 2 is greater than 25 degrees, as per ACI 318-14.')
            st.markdown('OK')


    
else: 
    # design_results = rc_beam_design(fc = concrete_strength, fy=yield_strength, b = b_stream, h=h_stream, Mu=)
    with tab2: 
        st.markdown('Based on given geometry, this is not considered a deep beam per ACI 318-14 9.9.1.1 Bernoulli Theory will be used for analysis/design')

             
    with tab3: 
        st.markdown('Based on given geometry, this is not considered a deep beam per ACI 318-14 9.9.1.1 Bernoulli Theory will be used for analysis/design')
        try: 
            design_results = rc_beam_design(concrete_strength, yield_strength, b_stream, h_stream, results['Mu'], results['Vu'], l_stream, tie_size_stream)
            st.markdown(f'Number of Bottom Bars Required = {design_results['Number of ties']}')
        except ZeroDivisionError:
             st.subheader('It looks like there is a zero division error, confirm all inputs are filled in')


     
















