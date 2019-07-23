#!/bin/bash

# List EIPs
# command to execute
cli_command='aws ec2 describe-addresses --query "Addresses[?AssociationId==null].[AllocationId]" --output text'
# profiles to use
cli_command_prod="$cli_command --profile prod"
cli_command_test="$cli_command --profile test"

# execute the commands
eip_list_prod="$(eval $cli_command_prod)"
echo "=== Unused EIPs in PROD account ==="
echo "${eip_list_prod}"

eip_list_test="$(eval $cli_command_test)"
echo "=== UNUSED EIPs in TEST account ==="
echo "${eip_list_test}"

# Release EIPs
# full command here as reference
# aws ec2 release-address --allocation-id eipalloc-0c355fb198eda4fdf --dry-run --profile prod
# command to execute (remove --dry-run to execute this)
cli_command='aws ec2 release-address --dry-run'
# profiles to use
cli_command_prod="$cli_command --profile prod"
cli_command_test="$cli_command --profile test"

echo ""
echo "The following EIPs used in PROD will be removed"
# loop and remove unused EIPs
for i in ${eip_list_prod}; do
    echo $i
    eval $cli_command_prod --allocation-id $i
done

echo ""
echo "The following EIPs used in TEST will be removed"
# loop and remove unused EIPs
for i in ${eip_list_test}; do
    echo $i
    eval $cli_command_test --allocation-id $i
done

