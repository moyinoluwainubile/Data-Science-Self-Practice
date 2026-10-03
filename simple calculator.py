def calculator():
    print("Welcome to my Simple Calculator")
    print("You can only perform simple addition, subtraction, multiplication, and division operations.")
    
    while True:
        # 1. Display the options menu
        print("\nPlease choose an operation:")
        print("1. Add (+)")
        print("2. Subtract (-)")
        print("3. Multiply (*)")
        print("4. Divide (/)")
        print("5. Exit")
        
        choice = input("Enter choice (1-5): ").strip()
        
        # Check if the user wants to close the program
        if choice == '5':
            print("Thank you for using the calculator. Goodbye!")
            break
            
        # Validate that a correct menu option was picked
        if choice not in ['1', '2', '3', '4']:
            print("Invalid choice! Please select a number from 1 to 5.")
            continue
            
        # 2. Get user numbers with safe validation loop
        while True:
            try:
                num1 = float(input("Enter first number: "))
                num2 = float(input("Enter second number: "))
                break  # Exit this internal loop if numbers are perfectly fine
            except ValueError:
                print("Invalid input! Please type actual numbers.")
        
        # 3. Perform the chosen mathematical operation
        if choice == '1':
            result = num1 + num2
            print(f"The result is: {num1} + {num2} = {result:.2f}")
            
        elif choice == '2':
            result = num1 - num2
            print(f"The result is: {num1} - {num2} = {result:.2f}")
            
        elif choice == '3':
            result = num1 * num2
            print(f"The result is: {num1} * {num2} = {result:.2f}")
            
        elif choice == '4':
            # Handle the specific runtime error of dividing by zero
            if num2 == 0:
                print("Error: Cannot divide by zero!")
            else:
                result = num1 / num2
                print(f"The result is: {num1} / {num2} = {result:.2f}")
        again = input("Would you like to perform another calculation? (yes/no): ").strip().lower()
        if again != 'yes':
            print("Thank you for using the calculator. Goodbye!")
            break

# Run the calculator function
calculator()