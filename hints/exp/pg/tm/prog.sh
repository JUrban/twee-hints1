#!/bin/bash
# $1 = goal: run its captured command with --progress 1, print the last PROGRESS line
w=$(grep "/$1.p " cmds.all); $w --progress 1 2>&1 | grep PROGRESS | tail -1
