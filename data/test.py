#!/usr/bin/python
import csv
import random

records=30
print("Making %d records\n" % records)

fieldnames=['id','name','age','city']
writer = csv.DictWriter(open("people.csv", "w"), fieldnames=fieldnames)

names=['Deepak', 'Sangeeta', 'Geetika', 'Anubhav', 'Sahil', 'Akshay']
cities=['Delhi', 'Kolkata', 'Chennai', 'Mumbai']

writer.writerow(dict(zip(fieldnames, fieldnames)))
for i in range(0, records):
  writer.writerow(dict([
    ('id', i),
    ('name', random.choice(names)),
    ('age', str(random.randint(24,26))),
    ('city', random.choice(cities))]))