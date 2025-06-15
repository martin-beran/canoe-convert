#!/bin/sh
CONV="python3 $(dirname $0)/eskymo123-conv.py"
for f in *_sl.csv; do
	C=$(echo $f | sed -E 's/.*_(...)_sl.csv/\1/' | tr '[a-z]' '[A-Z]')
	echo $C $f
	$CONV -c e2c -C "$C" "$f" "sl_$C.xml"
done
sed 's#<.*root>##' sl_* > sl.xml
