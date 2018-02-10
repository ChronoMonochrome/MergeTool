FILE=$1

if [ -z $FILE ]; then
	exit 1
fi

a=""
while [[ "$a" != "o" ]] && [[ "$a" != "t" ]] ; 
do
    echo "[o]urs or [t]heirs?" && read a
done

#echo $a
if [[ "$a" == "o" ]] ; then
	echo $FILE >> ours.txt
fi

if [[ "$a" == "t" ]] ; then
	echo $FILE >> theirs.txt
fi
