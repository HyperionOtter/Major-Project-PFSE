# IMPORTS 
import math
import plotly.express as px 
import streamlit as st

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




