print("Enter your name:")
name = input()
print(f"Hello {name}")

name = input("Enter your name:")
fav1 = input("What is your favorite animal:")
fav2 = input("What is your favorite color:")
fav3 = input("What is your favorite number:")
print(f"Hello {name}! Do you want a {fav2}, {fav1} with {fav3} legs?")

x=input("Enter a number:")
y=input("Enter another number:")
print(f"The sum of {x} and {y} is {float(x)+float(y)}.")

while True:
    x=input("Enter a number:")
    y=input("Enter another number:")
    try:
        x=float(x)
        y=float(y)
        break
    except:
        print("Wrong input, please try again!")
print(f"The sum of {x} and {y} is {x+y}.")