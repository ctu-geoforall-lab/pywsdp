@echo off
rem testovaci skript na spusteni skriptu ctios.py

setlocal

set parent=%~dp0..\
set VAR_1=WSTEST
set VAR_2=WSHESLO
set VAR_3="select id from opsub limit 10"
set VAR_4=%parent%tests\
set VAR_5=%parent%tests\input_data\Export_1-4.db

python %parent%ctios.py --user %VAR_1% --password %VAR_2% --sql %VAR_3% --logdir %VAR_4% --db %VAR_5%

pause