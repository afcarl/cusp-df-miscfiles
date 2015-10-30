#!/bin/bash
DATABASE=df_spatial
IFS="$(echo -e '\n\r')";
FILES=$(find -name "*.zip"); 
for FILE in $FILES
do 
    BASE=$(basename $FILE .zip)
    # next line returns "2010_09_tabblock10" from "tl_2010_09_tabblock10"
    TABLE=$( echo $BASE | sed 's/^[a-z]*_//g')
    # double check the extracted files have been cleaned up or zip will moan
    rm /tmp/${BASE}.*
    echo "$BASE to $TABLE"
    unzip -d /tmp $FILE
    MATCH=$(echo "\d" | psql ${DATABASE} | grep -o "${TABLE}")
    if [ "$MATCH" ]
    then
	# Append to the exisitng table
	echo "Appending to ${TABLE}"
	shp2pgsql -s 4326 -I -S -a -W UTF-8 "/tmp/${BASE}.shp" $TABLE | psql $DATABASE
    else
	# Create the table
	echo "Creating $TABLE"
	case shp2pgsql -s 4326 -I -S -c -W UTF-8 "/tmp/${BASE}.shp" $TABLE | psql $DATABASE
    fi
    # clean up
    rm /tmp/${BASE}.*          
done
