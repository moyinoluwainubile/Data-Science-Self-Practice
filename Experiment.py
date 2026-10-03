a=15
b=20
c=55
d=38
e=42
f=60

sum=a + b + c + d + e + f
print (sum)

if sum<=0:
    print ('Cannot calculate the average of 0 or negative numbers')
else:
    average=sum/6
    print ('The average of the numbers is:', round(average, 2))