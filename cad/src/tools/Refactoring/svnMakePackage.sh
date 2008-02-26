#!/bin/sh

svn mkdir $1
touch $1/__init__.py
svn add $1/__init__.py
