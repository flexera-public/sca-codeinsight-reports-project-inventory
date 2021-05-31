@echo off
rem ################################################################################
rem #  This test file allows the report script to be called as if it was being
rem #  called from the custom report framework to allow for script development
rem #  prior to registering the script with Code Insight

set projectId=8
set reportId=4
set authToken=eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJzZ2VhcnkiLCJ1c2VySWQiOjIsImlhdCI6MTYyMTMzNDc2NH0.TF91j0Aqbe0NAoiXtyoqpqNrn9nEU1y7nVura1nZ3od2s_Bt2DGuRwBqnNqycpNWRbq5FGZAkOSAW563t_On_g

set reportOptions="{""includeChildProjects"":""true"", ""cvssVersion"":""3.0""}"


./create_report.bat  %projectId%  %reportId%  %authToken%  %reportOptions%


