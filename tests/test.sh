#!/bin/sh

./ctios.py \
    --user WSTEST \
    --password WSHESLO \
    --logdir tests/ \
    --db tests/input_data/Export_1-4.db \
    --sql "SELECT ID FROM OPSUB LIMIT 10"

 #     --posidents tests/input_data/posidents_1-4.txt \

exit 0
