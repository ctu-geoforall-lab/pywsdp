#!/bin/sh

tmpdir=$(mktemp -u)
mkdir $tmpdir
cp tests/input_data/Export_1-4.db $tmpdir/
db=$tmpdir/Export_1-4.db

./ctios.py \
    --user WSTEST \
    --password WSHESLO \
    --logdir tests/ \
    --db $db \
    --sql "SELECT ID FROM OPSUB LIMIT 10"

rm -r $db

exit 0
