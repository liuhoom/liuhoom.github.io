#!/bin/bash

apath=/opt/pb/github/liuhoom.github.io
cd ${apath}

/opt/pb/py3/bin/python main.py

git add .
git commit -m `date +%s`
git push origin master
