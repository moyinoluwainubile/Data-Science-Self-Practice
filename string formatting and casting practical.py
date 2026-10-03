txt=f'the price is 10 dollars'
print(txt)

price=20.3467
txt=f'the price is {price} dollars'
print(txt)

txt=f'the price is {price:.2f} dollars'
print(txt)

txt=f'the price is {30.3467:.2f} dollars'
print(txt)

cprice=10
tax=0.25
txt=f'the price is {cprice+tax:.2f} dollars'
print(txt)

txt=f'the price is {10*2:.2f} dollars'
print(txt)

txt=f"it is very {'expensive' if cprice>10 else 'cheap'}"
print(txt)

lprice='twenty naira'
txt=f"the price is {lprice.title()}"
print(txt)