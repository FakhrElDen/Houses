from cs50 import SQL
from sys import argv, exit


if len(argv) != 2:
    print("Usage: python roster.py HouseName")
    exit(1)

HouseName = argv[1]
house = []
frist = []
middle = []
last = []
birth = []
num = 0

db = SQL("sqlite:///students.db")
for row in db.execute("SELECT house FROM students GROUP BY house"):
    house.append(row["house"])


def search(Tuple, n):
    flag = 0
    for i in range(len(Tuple)):
        if Tuple[i] == n:
            flag = 1
    if flag == 0:
        print("House Name is wrong it check it again")
        exit(1)


search(house, HouseName)


for row in db.execute("SELECT first, middle, last, birth FROM students WHERE house = '%s' ORDER BY last, first" %HouseName):
    frist.append(row["first"])
    middle.append(row["middle"])
    last.append(row["last"])
    birth.append(row["birth"])


while num < len(frist):
    if middle[num] == None:
        print(f"{frist[num]} {last[num]}, born {birth[num]}")
    else:
        print(f"{frist[num]} {middle[num]} {last[num]}, born {birth[num]}")
    num += 1