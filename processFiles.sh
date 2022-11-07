mkdir processed
for f in $1*;
do
    echo "Processing $f"
    awk '{gsub(/\t/,"\",\"")}1' $f > $f.1
    awk '{gsub(/$/,"\"")}1' $f.1 > $f.2
    awk '{gsub(/^/,"\"")}1' $f.2 > $f.3.csv
    rm $f.1
    rm $f.2
    mv $f processed
    echo "$f Complete"
done