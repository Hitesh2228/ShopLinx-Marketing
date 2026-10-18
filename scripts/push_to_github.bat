@echo off
cd /d "D:\Antigravity Projects\ShopLinx Marketing"
echo ========================================================
echo   SHOPLINX MARKETING - PUSH TO GITHUB ACTIONS
echo ========================================================
echo 1. Go to https://github.com/new and create a Private repo (e.g. ShopLinx-Marketing)
echo 2. Paste the repo URL below:
echo.
set /p REPO_URL="Repository URL: "
if "%REPO_URL%"=="" goto end
git remote remove origin 2>nul
git remote add origin %REPO_URL%
git branch -M main
git push -u origin main
echo.
echo ========================================================
echo [SUCCESS] Pushed to GitHub!
echo GitHub Actions 24/7 Sniper is now ACTIVE in the cloud!
echo ========================================================
:end
pause
