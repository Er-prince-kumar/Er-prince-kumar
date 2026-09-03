# 🚀 Prince Kumar's GitHub Jet Heatmap & Profile Setup Guide

This folder contains everything needed to transform your GitHub profile page ([github.com/Er-prince-kumar](https://github.com/Er-prince-kumar)) with an animated Cyber Terminal card and Jet Heatmap animation!

---

## 📁 What's Included

- `dark.svg` - Cyber Terminal animated profile card (Dark theme with ASCII portrait and system stats).
- `light.svg` - Cyber Terminal animated profile card (Light theme).
- `dist/github-jet.svg` - Animated fighter jet flying across your real GitHub contribution heatmap, shooting bullets at active days!
- `README.md` - Complete, stunning profile README with auto theme-switching, activity graphs, and featured projects.
- `generate_jet.py` - Python script to regenerate `dist/github-jet.svg` locally.
- `generate.mjs` - Node.js script used by GitHub Actions.
- `.github/workflows/jet-heatmap.yml` - Automated GitHub Actions workflow to update `github-jet.svg` daily.
- `setup_git.bat` - One-click deployment script to commit and push to GitHub.

---

## 🛠️ Step-by-Step Deployment

### Step 1: Create the Special Profile Repository on GitHub
1. Open [https://github.com/new](https://github.com/new) in your browser.
2. Under **Repository name**, enter: `Er-prince-kumar`
   *(GitHub will show a note: "You found a secret! Er-prince-kumar/Er-prince-kumar is a special repository that you can use to add a README.md to your GitHub profile.")*
3. Make sure **Public** is selected.
4. **Leave all checkboxes unchecked** (Do NOT add a README, .gitignore, or license, since we already created them).
5. Click **Create repository**.

---

### Step 2: Push to GitHub
Run the included `setup_git.bat` file, or run these commands in your terminal:

```bash
cd b:\bipul\portfolio\prince-profile-repo
git init
git branch -M main
git add .
git commit -m "Add Cyber Terminal profile cards and GitHub Jet Heatmap animation"
git remote add origin https://github.com/Er-prince-kumar/Er-prince-kumar.git
git push -u origin main
```

---

### Step 3: Enable GitHub Actions Permissions
To allow GitHub Actions to automatically update your Jet Heatmap daily:
1. In your `Er-prince-kumar` repository on GitHub, go to **Settings** → **Actions** → **General**.
2. Scroll down to **Workflow permissions**.
3. Select **"Read and write permissions"**.
4. Click **Save**.

---

### Step 4: Verify Your Profile!
Open [https://github.com/Er-prince-kumar](https://github.com/Er-prince-kumar) to view your animated, cybernetic profile!
