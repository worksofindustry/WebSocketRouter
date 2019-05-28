#!/bin/bash
clear

sudo kill -9 $(sudo lsof -t -i:80)
screen -X -S WSR quit