#!/usr/bin/env sh

unit="$1"
shift && poetry run tox -e "${unit}" -- -- "$@"
