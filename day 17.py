details = """My name is Moyinoluwa. 
I am learning Python programming and I am excited about it!
Well, 'I love Python because it is versatile and easy to learn.'
Give me food."""
print(details)

names = "Moyinoluwa Blessing Inubile"
print(names[0]) # prints the first character of the string

name = ["Moyinoluwa", "Blessing", "Inubile"]
for name in name:
    print(name) # prints each name in the list on a new line

print(len(names)) # prints the length of the string

print("Moyinoluwa" in names) # checks if "Moyinoluwa" is in the string and prints True
if "Moyinoluwa" in names:
    print("Yes, 'Moyinoluwa' is in the string.") # prints this message if the condition is True
print("Moyinoluwa" not in names) # checks if "Moyinoluwa" is not in the string and prints False
if "Seun" not in names:
    print("No, 'Seun' is not in the string.") # prints this message if the condition is True

print(names[:27]) # prints the first 27 characters of the string
print(names[2:20]) # prints characters from index 2 to 19 of the string
print(names[2:]) # prints characters from index 2 to the end of the string
print(names[-3:]) # prints the last three characters of the string
print(names[-27:-1]) # prints characters from index -27 to -2 of the string
print(names[:-7]) # prints characters from the start of the string to index -8

print(names.upper()) # prints the string in uppercase
print(names.lower()) # prints the string in lowercase
print(names.capitalize()) # prints the string with the first character in uppercase
print(names.title()) # prints the string with the first character of each word in uppercase

city = "    Lagos State  "
print(city.strip()) # prints the string with leading and trailing whitespace removed
print(names.replace("Moyinoluwa", "Pelumi")) # prints the string with "Moyinoluwa" replaced by "Pelumi"
print(names.split()) # prints the string split into a list of words
print("-".join(names.split())) # prints the string with "-" inserted between each character