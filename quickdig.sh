#! /bin/sh

for i in $(cat ./apps.txt); do
    echo $i >> ./io/apps-output.csv
    dig +short $i | head -n 1 >> ./io/apps-output.csv
done
