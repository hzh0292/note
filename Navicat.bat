@color a0
@title ����Navicat��������
@echo off
echo --------------------------
echo     ���ڹرս���...
echo --------------------------
taskkill /F /T /IM navicat.exe
if exist %temp%\backup.reg (
del %temp%\backup.reg
)
echo --------------------------
echo     ���ڱ���ע���...
echo --------------------------
reg EXPORT HKCU\Software %temp%\backup.reg
echo --------------------------
echo   ��������ע����ļ�...
echo --------------------------
set fr=-
echo Windows Registry Editor Version 5.00 >> %temp%\Navicat.reg
echo [-HKEY_CURRENT_USER\Software\PremiumSoft\Data] >>%temp%\Navicat.reg
for /F "delims=" %%i in ('"REG QUERY "HKEY_CURRENT_USER\Software\Classes\CLSID" /s | findstr /E Info"') do (
echo [%fr%%%i] >> %temp%\Navicat.reg
)
echo --------------------------
echo     ����ִ�в���...
echo --------------------------
regedit /s %temp%\Navicat.reg
echo --------------------------
echo   Navicat������������...
echo --------------------------
del %temp%\Navicat.reg
pause