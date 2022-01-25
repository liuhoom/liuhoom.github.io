#!/bin/bash

apath=/opt/pb/github/liuhoom.github.io
cd ${apath}

/opt/pb/py3/bin/python main.py

\cp index.html.js index.html

for filename in `ls -1 html`
do 
	name=`echo $filename | awk -F'.' '{print $1}'`
	str="<h2><a href="/html/${filename}">${name}</a></h2></br>"
	sed "/content/i ${str}" index.html -i
done

git add . -A
git commit -m `date +%s`
git push origin master
