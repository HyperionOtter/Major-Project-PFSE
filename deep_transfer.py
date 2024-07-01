# IMPORTS 
import plotly.express as px 
import plotly.graph_objects as go
import streamlit as st
from deep_transfer_app import deep_transfer_calc

# Streamlit UI 

st.markdown('# Deep Transfer Beam Design')
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


# Run Calculation 
results = deep_transfer_calc(P_DL=P_DL_stream, P_LL=P_LL_stream,l=l_stream,a=a_stream,h=h_stream,
                   b=b_stream,fc=concrete_strength,fy=yield_strength,tie_size=tie_size_stream,
                   stirrup_size=stirrup_size_stream, skin_size=skin_bar_size_stream,
                   stirrup_legs=stirrup_legs_stream,col1=c1_stream,col2=c2_stream)



# Plot Figures 


def create_plot(polygon, l):
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
        fig.update_layout(
            title="Beam Model",
            xaxis_title="Beam Span (ft)",
            yaxis_title="Beam Height (in)",
            showlegend=False,
            xaxis=dict(
                range=[-0, l],  # Specify the x-axis range
                scaleanchor="y",
                scaleratio=12,
            ),
            yaxis=dict(
                range = [0, l+5],
                scaleanchor="x",
                scaleratio=1,
            ),
        )
        return fig  




# Plot Beam Conceptual Model 
beam_poly = results['Beam Model']
beam_plot = create_plot(polygon = beam_poly, l = l_stream)
beam_fig = st.plotly_chart(beam_plot)


# Shear Diagram 
shear_fig = results['Shear Diagram']
shear_diagram = st.plotly_chart(shear_fig)

#Moment Diagram 
moment_fig = results['Moment Diagram']
moment_diagram = st.plotly_chart(moment_fig)


# Results Outputs 
st.markdown('**Number of Ties/Tension Bars Required:**')
st.markdown(results['Number of ties'])





