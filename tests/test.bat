@echo off
rem testovaci skript na spusteni skriptu ctios.py

setlocal

set parent=%~dp0..\
set VAR_1=WSTEST
set VAR_2=WSHESLO
set VAR_3="select id from opsub limit 100"
set VAR_4=%parent%tests\logy
set VAR_5=%parent%tests\input_data\Export_1-4.db

xcopy %VAR_5% %temp%

pause

python %parent%ctios.py --user %VAR_1% --password %VAR_2% --sql %VAR_3% --db %temp%\Export_1-4.db

pause