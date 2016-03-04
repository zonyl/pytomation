#!/bin/sh
[ -n "$1" ] && exec python -m unittest tests.$1
exec python -m unittest tests
