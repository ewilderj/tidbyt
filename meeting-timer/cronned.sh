#!/bin/bash
# just enough script to run OK on a cronjob
# update TIMERDIR to wherever you put this thing

TIMERDIR=$HOME/git/tidbyt/meeting-timer
cd $TIMERDIR
source venv/bin/activate
python update.py >timer.out
