#!/usr/bin/python
# -*- coding: utf-8 -*-

import cProfile
from dragoncreole import DragonCreole

parser = DragonCreole()

def DoTest(i):
	with open("test.txt", "r") as f:
		text = f.read()
	i = int(i)
	for x in range(i):
		parser.render(text)

cProfile.run("DoTest(1000)", sort=2)
