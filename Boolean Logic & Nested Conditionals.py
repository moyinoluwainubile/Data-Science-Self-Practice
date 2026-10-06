age = int(input("Enter your age: "))
# Nested Version
if age >= 18:
    has_id = input("Do you have an ID? (yes/no): ").lower() == "yes"
    if has_id:
        print("You are eligible to vote.")
    else:
        print("You need an ID to vote.")
else:
    print("You are not eligible to vote.")

# Equivalent Compound Version
if age >= 18 and input("Do you have an ID? (yes/no): ").lower() == "yes":
    print("You are eligible to vote.")
else:
    print("You are not eligible to vote.")

# Guided Practice
password = "abc123"
has_length = len(password) >= 8 # Checks length of Password
has_number = any(char.isdigit() for char in password) # checks if number is in password
print(has_length)
print(has_number)
print(has_length and has_number)