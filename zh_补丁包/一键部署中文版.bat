@echo off
rem ============================================
rem  AI中割 中文补丁包 一键部署
rem  用法：把整个补丁包文件夹放到 MikuMikuDance.exe 同目录，双击本文件。
rem ============================================
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

rem 包可能整个放在 MMD 目录里（此时 MMD exe 在上一级），也可能 bat 与 exe 同目录。两种都支持
set "ROOT=%~dp0"
if not exist "%ROOT%MikuMikuDance.exe" for %%I in ("%~dp0..") do set "ROOT=%%~fI\"
if not exist "%ROOT%MikuMikuDance.exe" (
  echo [错误] 没有找到 MikuMikuDance.exe。
  echo.
  echo        请把整个补丁包文件夹放到 MikuMikuDance.exe 的同一目录里，再双击本文件。
  pause
  exit /b 1
)

echo 补丁包位置: %~dp0
echo 检测到 MMD : %ROOT%
echo.

rem ---- 前置检查 ----
if not exist "%ROOT%MMD-AINakawari\app\mmd_ainakawari\app.py" (
  echo [错误] 未安装原版 MMD-AINakawari。
  echo.
  echo        这里没有找到: %ROOT%MMD-AINakawari\app\
  echo        请先按 README_Zh.md 的「安装」一节装好官方发行版 zip，
  echo        再把本补丁包放回 MikuMikuDance.exe 同目录重新双击。
  pause
  exit /b 1
)

if not exist "%ROOT%Plugin\MMD-AINakawari" (
  echo [错误] 未安装原版 MMD-AINakawari。
  echo.
  echo        找到了 AI 本体，但没有 %ROOT%Plugin\MMD-AINakawari\
  echo        （MMD 加载用的 DLL 目录）。请先完整装好官方发行版 zip 再运行本工具。
  pause
  exit /b 1
)

if not exist "%~dp0MMD-AINakawari.dll" (
  echo [错误] 补丁包里缺少 MMD-AINakawari.dll，请确认补丁包完整。
  pause
  exit /b 1
)

tasklist /fi "imagename eq MikuMikuDance.exe" 2>nul | find /i "MikuMikuDance.exe" >nul
if not errorlevel 1 (
  echo [错误] MMD 正在运行。请先关闭 MMD 再运行本工具（否则文件无法替换）。
  pause
  exit /b 1
)

echo 检查通过，开始部署中文补丁...
echo.

rem ---- 第 1 步：第一次部署时给每个被覆盖的文件留 .orig 备份 ----
set "BAK=0"
for %%F in (
 "app\mmd_ainakawari\__init__.py"
 "app\mmd_ainakawari\i18n.py"
 "app\mmd_ainakawari\zh_compat.py"
 "app\mmd_ainakawari\mmd_link.py"
 "app\mmd_ainakawari\mmm_link.py"
 "app\mmd_ainakawari\app.py"
 "app\mmd_ainakawari\panel.py"
 "app\mmd_ainakawari\samples.py"
 "app\mmd_ainakawari\prompt_samples.txt"
 "app\mmd_ainakawari\installer\window.py"
 "app\mmd_ainakawari\texts\zh_all.py"
 "app\tools\install_plugin.py"
) do (
  if exist "%ROOT%MMD-AINakawari\%%~F" if not exist "%ROOT%MMD-AINakawari\%%~F.orig" (
    copy /y "%ROOT%MMD-AINakawari\%%~F" "%ROOT%MMD-AINakawari\%%~F.orig" >nul
    set /a BAK+=1
  )
)
echo 已备份原版文件: !BAK! 个（同名 .orig）
rem ---- 第 2 步：把 app 里的中文文件按原路径合并进去（只覆盖包里有的文件） ----
xcopy /e /y /q /i "%~dp0app" "%ROOT%MMD-AINakawari\app\" >nul
if errorlevel 1 (
  echo [错误] 复制中文文件失败，请确认没有文件被占用后重试。
  pause
  exit /b 1
)

rem ---- 第 3 步：替换 DLL ----
copy /y "%~dp0MMD-AINakawari.dll" "%ROOT%Plugin\MMD-AINakawari\MMD-AINakawari.dll" >nul
if errorlevel 1 (
  echo [错误] 替换 DLL 失败。请确认 MMD 已关闭后重试。
  pause
  exit /b 1
)

rem ---- 第 4 步：字节级验收（不复核就报成功等于没验收） ----
set "FAIL=0"
if not exist "%ROOT%MMD-AINakawari\app\mmd_ainakawari\zh_compat.py" set "FAIL=1"
if not exist "%ROOT%MMD-AINakawari\app\mmd_ainakawari\texts\zh_all.py" set "FAIL=1"
fc /b "%~dp0MMD-AINakawari.dll" "%ROOT%Plugin\MMD-AINakawari\MMD-AINakawari.dll" >nul
if errorlevel 1 set "FAIL=1"
if "%FAIL%"=="1" (
  echo [错误] 部署后验收失败（文件不齐或 DLL 不一致）。
  echo        请截图本窗口，连同 app\work\app.log 一起反馈。
  pause
  exit /b 1
)

echo.
echo ====== 部署完成，验收通过 ======
echo   中文界面文件 : 12 个已就位（原版备份为同名 .orig）
echo   中文 DLL     : Plugin\MMD-AINakawari\MMD-AINakawari.dll 已替换（字节校验一致）
echo.
echo 现在可以打开 MMD：菜单栏「帮助」右边应出现「AI中割」，
echo 右下角出现「AI中割 简易操作」中文面板。
echo 插件完整中文说明见补丁包里的 README_Zh.md。
echo.
pause
