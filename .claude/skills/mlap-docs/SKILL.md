---
name: mlap-docs
description: Change, verify and ship MLAP documentation. Use for any edit under docs/, mkdocs.yml or overrides/ — building the site strictly, checking claims against the archive, and the branch → PR → merge → sync loop across the LLNL repo and the pkjha fork. Also use when asked to "switch to latest dev, push to pkjha, and delete feature branches".
---

# Shipping MLAP documentation

## 1. Build and verify

`mkdocs` is not installed globally. Create the venv once — `.venv/` is already
gitignored — and reuse it:

```bash
python3 -m venv .venv
.venv/bin/pip install -q -r requirements-docs.txt
```

Build strictly after every change, into a throwaway directory:

```bash
.venv/bin/mkdocs build --strict -d /tmp/mlap-site
```

`--strict` is not optional. It is what catches broken internal links and
anchors, and anchors break easily:

- Renaming a heading changes its slug and silently breaks inbound links.
- Removing `###` subheadings removes their anchors. Grep for inbound references
  **before** the edit, not after.
- Python-Markdown slugs strip punctuation: "the author's skills" →
  `the-authors-skills`.

For layout or styling changes, confirm the result in the built HTML rather than
assuming. The built `assets/stylesheets/main.*.min.css` is also the fastest way
to check what Material's own rules are before overriding them — `extra.css`
loads last, so equal specificity wins, but a more specific theme rule does not.

## 2. Check claims before writing them

Documentation here is evidence-based, and that is its value. Figures come from
reading the source or `ForClaude/Wildfire_Results/`, never from recall:

| To establish | Read |
|---|---|
| Collections, counts, dataset indices | `ForClaude/Wildfire_Results/Output/Step4_Eval`, `Step3_Train` |
| Input configurations as archived | `ForClaude/Wildfire_Results/InputJson/` |
| What the code actually does | The `.py` under `MachineLearningAutomationPipleline/` |

If a claim cannot be checked, say so in the text rather than asserting it. When
a colour or contrast is involved, compute the ratio; when a numerical claim is
involved, measure it with the pipeline's own coefficients and dtypes.

Keep implementation-quality material off the published site. It is the author's
to publish, lives in the gitignored `IMPROVEMENT_SCOPE.md`, and the score card
is scoped to automation design.

## 3. Branch and commit

Never commit to `development`. Branch first, named for the change:

```bash
git checkout -b docs-<subject>
```

Imperative subject line; body explains *why*, including what was measured or
verified and anything left undone. End with:

```
Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
```

Split unrelated changes into separate commits even when they touch one file —
stage by hunk, or reconstruct the intermediate state. A commit that changes only
comments is worth isolating, and worth proving: compare `ast.dump()` before and
after.

## 4. Pull request

PRs go to the **LLNL** repo with the head on the **fork**:

```bash
git push -u pkjha <branch>
gh pr create --repo LLNL/MLAP --base development \
             --head pkjha-aero:<branch> --title "..." --body "..."
```

End the body with:

```
🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

Put anything the reviewer must decide into the body — unverified facts,
judgement calls, behaviour changes that were not exercised. That is where they
survive the merge.

## 5. After the merge

Triggered by "switch to latest dev, push to pkjha, and delete feature branches":

```bash
gh pr view <n> --repo LLNL/MLAP --json state,mergedAt   # confirm merged first
git fetch llnl
git checkout development
git merge --ff-only llnl/development                    # never a merge commit
git push pkjha development
```

Then delete the branch, after confirming it holds nothing unique:

```bash
git merge-base --is-ancestor <branch> development       # must pass
git branch -D <branch>
git push pkjha --delete <branch>
```

Report the final branch state on both remotes and confirm zero divergence.

## Hard rules

- **Never delete `gh-pages`** on either remote. It is the deployed site, not a
  feature branch. Exclude it from every branch-cleanup sweep, along with
  `development` and `master`.
- **Never rename a branch that is already pushed and has an open PR.** GitHub
  does not retarget a cross-fork head ref — it closes the PR, and it cannot be
  reopened. Renaming closed PR #29 this way. To rename, close and open a fresh
  PR deliberately, or leave the name alone.
- Verify a branch is an ancestor of `development` before deleting it. Deleting a
  remote branch is not recoverable from here.
- After deploying, the site is cached for about ten minutes. "It didn't update"
  is usually a stale cache — check the built HTML on `gh-pages` before believing
  a bug report.
