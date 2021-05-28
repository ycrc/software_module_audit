awk -F : 'NF {printf "hide_version('\''%s'\'') -- deprecating\n", $1}' admin.list
