#!/bin/bash

echo "APP_ENV is $APP_ENV"
app_env=$APP_ENV

if [ ! -n "$app_env" ]; then
  echo "default app env dev"
  . ./env.sh
elif [ "$app_env" = "dev" ]; then
  echo "app env dev"
  . ./env.sh
elif [ "$app_env" = "prod" ]; then
  echo "app env dev"
  . ./prodenv.sh
elif [ "$app_env" = "stg" ]; then
  echo "app env stg"
  . ./stgenv.sh
elif [ "$app_env" = "test" ]; then
  echo "app env test"
  . ./testenv.sh
fi

echo "rm env file"
rm *env.sh

set
