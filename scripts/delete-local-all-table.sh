#!/usr/bin/env bash
set -Ceuo pipefail
cd `dirname $0`

tables=$(aws --endpoint-url=http://localhost:8000 dynamodb list-tables | jq -r ".TableNames[]")

echo -n "now deleting"
for table in ${tables}; do
    echo -n "."
    aws --endpoint-url=http://localhost:8000 dynamodb delete-table \
        --table-name ${table} > /dev/null
done
echo ""
echo ""
echo "delete completed."





