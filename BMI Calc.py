name = input("What is your name?")
print(f"Hello {name}!")

weight = input("Enter your weight in kg:")      # This line prompts the user to enter their weight in kilograms and stores it in the variable 'weight'.
height = input("Enter your height in meters:")  # This line prompts the user to enter their height in meters and stores it in the variable 'height'.
weight = float(weight)                          # This line converts the string input for weight into a float and stores it back in 'weight'.
height = float(height)                          # This line converts the string input for height into a float and stores it back in 'height'.
bmi = weight / (height ** 2)                    # This line calculates the BMI using the formula weight divided by height squared and stores it in the variable 'bmi'.
print(f"Your BMI is: {bmi:.1f}")                # This line prints the calculated BMI rounded to one decimal place.

# Stretch Task: Classification Print for BMI categories based on the calculated BMI value.
if bmi < 18.5:                                  # This line checks if the BMI is less than 18.5, which indicates underweight.
    print("You are underweight.")               # If the condition is true, it prints that the user is underweight.
elif bmi >= 18.5 and bmi < 25:                  # This line checks if the BMI is between 18.5 and 25, which indicates a normal weight.
    print("You have a normal weight.")          # If the condition is true, it prints that the user has a normal weight.
else:                                           # This line handles all other cases, indicating overweight.
    print("You are overweight.")                # If the condition is true, it prints that the user is overweight.