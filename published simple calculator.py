import streamlit as st

# App title and description
st.title("🔢 Simple Calculator")
st.write("You can perform simple addition, subtraction, multiplication, and division operations.")

# 1. Get user numbers using visual numeric inputs
# Streamlit's number_input only allows actual numbers, making try/except loops unnecessary!
num1 = st.number_input("Enter first number:", value=0.0, format="%.2f")
num2 = st.number_input("Enter second number:", value=0.0, format="%.2f")

# 2. Display the operations menu as a clean dropdown selector
operation = st.selectbox(
    "Please choose an operation:",
    ["Add (+)", "Subtract (-)", "Multiply (*)", "Divide (/)"]
)

# 3. Perform the chosen mathematical operation when the button is clicked
if st.button("Calculate", type="primary"):
    if operation == "Add (+)":
        result = num1 + num2
        st.success(f"**Result:** {num1} + {num2} = {result:.2f}")
        
    elif operation == "Subtract (-)":
        result = num1 - num2
        st.success(f"**Result:** {num1} - {num2} = {result:.2f}")
        
    elif operation == "Multiply (*)":
        result = num1 * num2
        st.success(f"**Result:** {num1} * {num2} = {result:.2f}")
        
    elif operation == "Divide (/)":
        # Handle the specific runtime error of dividing by zero gracefully
        if num2 == 0:
            st.error("Error: Cannot divide by zero!")
        else:
            result = num1 / num2
            st.success(f"**Result:** {num1} / {num2} = {result:.2f}")
