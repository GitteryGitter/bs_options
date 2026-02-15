import os

os.system("clear")
os.system("./ASCII_animations/donut")
os.system("clear")

with open('intro.txt', mode='r') as f:
    text = f.read()

print(text)

choice = int(input())

assert choice in [1, 2, 3]

if choice == 1:
    os.system("./ASCII_animations/donut")
elif choice == 2:
    os.system("./ASCII_animations/fire")
else:
    os.system("./ASCII_animations/fireworks")

os.system("clear")
os.system("./ASCII_animations/success")