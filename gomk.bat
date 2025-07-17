@echo off
chcp 65001 > nul 2>&1
doskey cat=type $*
doskey cp=copy $*
doskey ls=dir /w $*
echo 이제 UTF-8 명령창입니다.
