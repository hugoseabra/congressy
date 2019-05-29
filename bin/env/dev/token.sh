#!/bin/bash

if [ -z "$1"  ]
  then
    echo -e "USAGE: \n\n $0 username(email) \n"
		exit 1;
fi


if [ -n "`$SHELL -c 'echo $ZSH_VERSION'`" ]; then
	FILE="$HOME/.zshrc"
elif [ -n "`$SHELL -c 'echo $BASH_VERSION'`" ]; then
	FILE="$HOME/.bashrc"
else
  	echo "Unknown $SHELL. Fix me to add support.";
        exit 1;	
fi





TOKEN="$(python manage.py drf_create_token $1  | cut -d ' ' -f 3)";

echo "Setting VUE_APP_REST_TOKEN to $TOKEN on $FILE";
sed -i '/export VUE_APP_REST_TOKEN=*/d' $FILE;
echo "export VUE_APP_REST_TOKEN=$TOKEN" >> $FILE;
