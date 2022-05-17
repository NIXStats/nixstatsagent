@echo off

"%~dp0python\python.exe" -W ignore::DeprecationWarning "%~dp0..\src\agent360.py" %*
