@echo off
rem Build Chinese-patched MMD-AINakawari.dll.
rem Uses a temporary copy of mmd_plugin.h with WndProc signature adjusted to match
rem MMD-AINakawari's source (official dev SDK is non-const; MMDZh's header is const).
rem Output: mmd_plugin\bin\MMD-AINakawari.dll -> copy to MMD\plugin\MMD-AINakawari\
setlocal
cd /d "%~dp0..\.."
set "VC=D:\MMD\VS\msvc_builder_v14.37.32822_Portable_by_pkups@wy\vs_builder\vc.bat"
if not exist "%VC%" (echo Portable MSVC not found, edit VC= in this file & exit /b 1)
call "%VC%" >nul
if errorlevel 1 (echo MSVC env failed & exit /b 1)

set "SDK=%~dp0..\..\..\MMDZh\lib"
if not exist "%SDK%\mmd_plugin.h" set "SDK=%~dp0..\..\..\..\MMDZh\lib"
if not exist "%SDK%\mmd_plugin.h" (echo mmd_plugin.h not found & exit /b 1)

set "BUILDSDK=%~dp0..\..\work\mmdplugin\dev"
if not exist "%BUILDSDK%" mkdir "%BUILDSDK%"
copy /Y "%SDK%\mmd_plugin.h" "%BUILDSDK%\mmd_plugin.h" >nul
copy /Y "%SDK%\MMDPlugin.lib" "%BUILDSDK%\MMDPlugin.lib" >nul
rem MMD-AINakawari uses WndProc(CWPSTRUCT*) [no const]; local headers use const.
powershell -NoProfile -Command "(Get-Content -LiteralPath '%BUILDSDK%\mmd_plugin.h' -Encoding UTF8) -replace 'WndProc\(const CWPSTRUCT\* param\)', 'WndProc(CWPSTRUCT* param)' | Set-Content -LiteralPath '%BUILDSDK%\mmd_plugin.h' -Encoding UTF8"
if errorlevel 1 (echo header patch failed & exit /b 1)

rem Output to repo root (writable) to avoid ACL issues with nested bin directories.
rem (cd /d "%~dp0..\.." above already set CWD to the repo root.)
cl /nologo /EHsc /LD /W3 /O2 /MT /utf-8 /std:c++14 ^
   /DUNICODE /D_UNICODE /DMAKE_MMD_PLUGIN /D_SILENCE_EXPERIMENTAL_FILESYSTEM_DEPRECATION_WARNING ^
   /I"%BUILDSDK%" ^
   mmd_plugin\nakawari_plugin.cpp mmd_plugin\nakawari_panel.cpp ^
   /Fo".\\" /Fe".\MMD-AINakawari.dll" ^
   /link /LIBPATH:"%BUILDSDK%" MMDPlugin.lib user32.lib gdi32.lib shlwapi.lib kernel32.lib
if errorlevel 1 (echo *** BUILD FAILED *** & exit /b 1)
echo.
echo *** OK: MMD-AINakawari.dll at repo root ***
echo Copy it to ^<MMD folder^>\plugin\MMD-AINakawari\MMD-AINakawari.dll
