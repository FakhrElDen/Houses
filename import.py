from cs50 import SQL
from sys import argv, exit
from csv import reader
from csv import DictReader


if len(argv) != 2:
    print("Usage: python import.py characters.csv")
    exit(1)


csvfile = argv[1]
num = 0
house = []
birth = []
names = []
db = SQL("sqlite:///students.db")

with open(csvfile, 'r') as read_obj:
    csv_reader = reader(read_obj)
    header = next(csv_reader)
    if header != None:
        for row in csv_reader:
            names.append(row[0])
            house.append(row[1])
            birth.append(row[2])


while num < len(names):
    student_id = num + 1
    student_house = house[num]
    student_birth = birth[num]
    full_name = names[num].rsplit(" ")
    if len(full_name) == 2:
        first_name = full_name[0]
        middle_name = None
        last_name = full_name[1]
    if len(full_name) == 3:
        first_name = full_name[0]
        middle_name = full_name[1]
        last_name = full_name[2]
    db.execute("INSERT INTO students (id, first, middle, last, house, birth) VALUES (?, ?, ?, ?, ?, ?) ",
               (student_id, first_name, middle_name, last_name, student_house, student_birth))
    num += 1