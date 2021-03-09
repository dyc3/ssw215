#!/usr/bin/env python3
import random
import string

def randstring():
	return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(random.randint(5, 14)))

for _ in range(5):
	print(f"INSERT INTO students (StudID, FirstName, LastName, Major, Year) VALUES ({random.randint(1, 98233299)}, '{randstring()}', '{randstring()}', '{randstring()}', {random.randint(1, 98233299)});")