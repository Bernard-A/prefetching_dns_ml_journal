#!/bin/bash


for i in "1" "2" "3"
do
	for j in "A" "B"
	do
		for k in "a" "b" "c" 
		do
			for l in "X" "L"
			do
				python pattern.py $i$j$k$l
			done
		done
	done
done
