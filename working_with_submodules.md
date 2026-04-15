# Git Submodule Update Workflow

## Updating Submodules

**After cloning a repo with submodules:**
```bash
git submodule update --init --recursive
```

**Pulling latest changes (parent repo + all submodules):**
```bash
git pull --recurse-submodules
```

**Updating a submodule to its latest remote commit:**
```bash
git submodule update --remote <submodule-path>
# or update all at once:
git submodule update --remote
```

---

## The Full Update Workflow

1. **Navigate into the submodule** and treat it like a normal repo:
   ```bash
   cd my-submodule
   git checkout main
   git pull origin main
   cd ..
   ```

2. **The parent repo now sees a new commit** in the submodule. Stage it:
   ```bash
   git add my-submodule
   ```

3. **Commit the pointer update** in the parent repo:
   ```bash
   git commit -m "Update my-submodule to latest"
   ```

4. **Push** the parent repo:
   ```bash
   git push
   ```

---

## Key Concepts

- A submodule is just a **pointer (SHA)** to a specific commit in another repo — the parent repo tracks *which commit*, not the files themselves.
- `git submodule update` checks out the **pinned commit** (what the parent expects), while `--remote` fetches and checks out the **latest** from the remote branch.
- Forgetting to commit after updating a submodule leaves the parent repo in a "dirty" state.

---

## Useful Commands

| Command | Purpose |
|---|---|
| `git submodule status` | See current state of all submodules |
| `git submodule foreach git pull` | Pull latest in every submodule |
| `git clone --recurse-submodules <url>` | Clone with submodules initialized |
| `git diff --submodule` | See what changed in submodules |

> **Common gotcha:** Teammates pulling your changes also need to run `git submodule update --init --recursive` after a pull that includes submodule pointer changes.