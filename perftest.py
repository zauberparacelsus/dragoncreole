#!/usr/bin/python3
# -*- coding: utf-8 -*-

import cProfile
from dragoncreole import DragonCreole

parser = DragonCreole()

def DoTest(i):
	with open("dragoncreole/test.txt", "r") as f:
		text = f.read()
	i = int(i)
	for x in range(i):
		parser.render(text)

cProfile.run("DoTest(1000)", sort=2)
