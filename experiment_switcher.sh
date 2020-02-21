#!/bin/bash

# run this script in the parent folder of the git repo!


function run_experiment() {
	cd source
	PYTHONPATH=../ python experiment_runner.py $1
	cd ..
}

cd gwynt
branches=( "mcts" )
for branch in "${branches[@]}"
do
	git checkout $branch
	run_experiment $branch
done

tput setaf 2
cat << "EOF"
______ _       _     _              _   _  
|  ___(_)     (_)   | |            | | | | 
| |_   _ _ __  _ ___| |__   ___  __| | | | 
|  _| | | '_ \| / __| '_ \ / _ \/ _` | | | 
| |   | | | | | \__ \ | | |  __/ (_| | |_| 
\_|   |_|_| |_|_|___/_| |_|\___|\__,_| (_)
EOF
tput sgr0
