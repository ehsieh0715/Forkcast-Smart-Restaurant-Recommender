## Github Workflow Guide
### Tips ‼️
- **Please always pull latest `dev` before starting a new task**
- **Please DO NOT commit directly to `main`**
- Before merge to dev, create pull Request and ask the team member to test or review the code

### Branch Structure
```
Branch Structure/
└── main ← final delivery
    │
    └── dev  ← merge from all team branches
        │
        ├── front-end/heatmap ← Work, commit, push, PR
        ├── back-end/feature-1  ← Work, commit, push, PR
        ├── data/settingDatabase  ← Work, commit, push, PR
        └── etc.
```

### Workflow
#### 1. Clone the Repositroy
- move to your local folder in terminal 
- clone the github repository 
```
git clone https://github.com/Justetete/COMP47360_Summer_Project_Group5.git
cd COMP47360_Summer_Project_Group5
```
#### 2. Create a New Branch from `dev`
```
git checkout dev
git pull origin dev
git checkout -b front-end/***
```
#### 3. Make changes and Commit in your local branch
> **Please commit often with clear messages!**
```
git add .
git commit -m "Add map UI with layout structure"
```
#### 4. Push your feature-branch to GitHub (remote feature branch)
```
git push origin front-end/heatmap
```
---

#### 5. Create a Pull Request (PR)
If you want to merge to the `dev` branch, firstly keep the `dev` branch updated
```
git checkout dev
git pull origin dev
git checkout frontend/map_ui

// Coding...

git rebase dev // Merge your feature's code to the updated dev branch
```

Then create a pull request 

1. Go to GitHub repository.
2. Click **“Compare & pull request”**.
3. Set:
- Base: `dev`
- Head: your feature branch
4. Add a title and description.
5. Click **Create Pull Request**.

#### 6. Review and Merge
- Ask team member reviews the PR
- Click `file change` button in the nav bar in PR page
- Review the code which will merge to dev branch, writing down your review in `Review changes` section in right side
- Click `Approve` and then click `submit review`, **merge into `dev`**

---
