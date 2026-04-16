@echo off
REM =====================================================================
REM  Strategic Plan Dashboard — Drupal integration demo launcher
REM
REM  Double-click this file to:
REM    1. Start a local web server on port 8765 (in the project root).
REM    2. Open the landing page and a pillar page in your default browser.
REM
REM  Leave the console window open during the demo. Close it (or press
REM  Ctrl+C) to stop the server. Nothing is installed; the server
REM  only runs while this window is open.
REM =====================================================================

REM Jump up from drupal-delivery\_test\ to the project root so the
REM server can serve /drupal-delivery/ AND the sibling /images/,
REM /data/ tree if you want to compare against the original site.
cd /d "%~dp0..\.."

echo.
echo ============================================================
echo   Strategic Plan Dashboard — Drupal Demo
echo ============================================================
echo.
echo   Serving at: http://localhost:8765
echo.
echo   Two browser tabs will open in a moment:
echo     - http://localhost:8765/drupal-delivery/_test/landing.html
echo     - http://localhost:8765/drupal-delivery/_test/pillar.html?p=2
echo.
echo   Keep this window open for the whole demo.
echo   Close it (or press Ctrl+C) to stop the server.
echo.
echo ============================================================
echo.

REM Schedule the browser tabs to open 2 seconds after the server
REM starts (give Python time to bind the port). Then start the
REM server in the foreground so closing this window stops it.
start "" cmd /c "timeout /t 2 /nobreak > nul && start "" http://localhost:8765/drupal-delivery/_test/landing.html && timeout /t 1 /nobreak > nul && start "" http://localhost:8765/drupal-delivery/_test/pillar.html?p=2"

python -m http.server 8765
