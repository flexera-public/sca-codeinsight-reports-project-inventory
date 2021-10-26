@echo off
rem ################################################################################
rem #  This test file allows the report script to be called as if it was being
rem #  called from the custom report framework to allow for script development
rem #  prior to registering the script with Code Insight

set projectId=5
set reportId=12
set authToken=eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJzZ2VhcnkiLCJ1c2VySWQiOjIsImlhdCI6MTYzMjI2MjU4MX0.M1-UkOnwfiuNgjF1A05CAyrr44DrHvPOie2tcpLn99dIrXJTo-GLsXvh1BXGbl5IgwkMjFpfPsESB3izKi0PzA

set reportOptions="{""includeChildProjects"":""t"", ""includeComplianceInformation"":""t"", ""maxVersionsBack"":""10"",""cvssVersion"":""3.0""}"


./create_report.bat  %projectId%  %reportId%  %authToken%  %reportOptions%


