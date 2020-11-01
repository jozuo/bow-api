#!/usr/bin/env bash
set -Ceuo pipefail
cd `dirname $0`
cd ..

if [ -d .dynamodb ]; then
  mkdir -p ./.dynamodb-data/
  sls dynamodb start --stage local &
  npx dynamodb-admin &
fi

