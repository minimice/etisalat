
#!/bin/bash

# Read blacklisted-ips.txt
# Loop through line by line
# Store each IP in the object
# 
# ip_set_descriptor {
#   type  = "IPV4"
#   value = ""
# }
#
# Save the object in a file 


# dev env
input="./blacklisted-ips.txt"

while IFS= read -r line
do
  echo 'ip_set_descriptor {' >> result.txt
  echo '  type  = "IPV4"' >> result.txt
  echo '  value  = "'${line}'/32"' >> result.txt
  echo '}' >> result.txt
  echo ' ' >> result.txt
done < "$input"

echo "Done"
