@echo off
echo =======================================================
echo  Deploying Prince Kumar's GitHub Profile Repository
echo  Target: https://github.com/Er-prince-kumar/Er-prince-kumar
echo =======================================================
echo.

if not exist ".git" (
    echo [*] Initializing git repository...
    git init
    git branch -M main
) else (
    echo [*] Git repository already initialized.
)

echo [*] Adding files...
git add .

echo [*] Committing files...
git commit -m "Add Cyber Terminal profile cards and GitHub Jet Heatmap animation"

echo.
echo [*] Checking remote origin...
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    echo [*] Setting remote origin to https://github.com/Er-prince-kumar/Er-prince-kumar.git
    git remote add origin https://github.com/Er-prince-kumar/Er-prince-kumar.git
) else (
    echo [*] Remote origin already set.
)

echo.
echo =======================================================
echo [*] Pushing to GitHub (main branch)...
echo =======================================================
git push -u origin main

echo.
echo Done! If push succeeded, your profile at https://github.com/Er-prince-kumar is now live!
pause
