# Factory lessons

Four mistakes the factory repeated in the first run (2026-11-01). Each cost a wave.

## 1. Invalid `gh pr view` field halts the run

- **Symptom:** three failed reads, then `github-halt.json` stops the run.
- **Cause:** `gh pr view --json threads` is not a valid field. A failed read counts toward the halt limit.
- **Fix:** read review threads with GraphQL and `reviewThreads` (`gh api graphql`). Use only valid `gh pr view --json` fields.

## 2. A card with an old branch is treated as a rebase

- **Symptom:** the Builder picks the rebase path and needs `mattpocock-skills:resolving-merge-conflicts`. That skill is missing from `mattpocock-skills` 1.3.1, so the card stalls.
- **Cause:** the issue branch already exists, so the Builder continues from it.
- **Fix:** rename the old branch to `archive/issue-<N>-<slug>-v1`, remove its clean worktree, then rebuild fresh.

## 3. `python3 -m pytest` fails on the merge gate PATH

- **Symptom:** the verify step reports no pytest module.
- **Cause:** only the repo `.venv` has pytest. The gate runs in a scratch worktree with the system `python3`.
- **Fix:** `verify_commands` resolves `.venv` through `git rev-parse --git-common-dir` and falls back to `python3`.

## 4. Two cards that touch `README.md` conflict

- **Symptom:** the second card to merge fails the gate with a merge conflict.
- **Cause:** both cards edit the same file and the first one merged.
- **Fix:** run cards that touch the same file in separate waves.
