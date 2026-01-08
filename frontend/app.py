import streamlit as st
import pandas as pd


st.title("NeuroFlow")
st.write("Hello World!")

st.header("1. DataFrame")
df = pd.DataFrame({
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [25, 30, 35],
    'City': ['New York', 'San Francisco', 'Los Angeles']
})

st.dataframe(df)  # Interactive table



st.header("2. Widgets")
if st.button("Click Me"):
    st.success("I was clicked!")

age = st.slider("How good is this app?", 0, 10, 10)
st.write(f"This app is {age}/10")

dis = st.text_input("Your disability is: ", "ADHD")
st.write(f"You have {dis}")



st.header("3. Layouts")

st.sidebar.header("Settings")
theme = st.sidebar.selectbox("Choose a theme", ["Light", "Dark", "System"])

col1, col2 = st.columns(2)

with col1:
    st.info("This is col1")
    st.metric(label="Temperature", value="27", delta='0.4')

with col2:
    st.info("Hello")
    st.metric(label="Humidity", value="60%", delta="-5%")