#! /bin/sh

OUTPUT=$1

echo "" > $OUTPUT

find ${CMSSW_BASE}/src/cp3_llbb -maxdepth 1 -type d |
while read dir
do
    if [ -e ${dir}/src/classes.h ]; then
        echo "#include <${dir}/src/classes.h>" >> $OUTPUT
    fi
done
