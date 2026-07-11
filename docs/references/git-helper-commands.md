# Git Helper Commands

## Status

Active

## Purpose

Document the durable behavior and implementation constraints for the repository's custom Git helper commands:

- `git-quick-push`
- `git-create-branch`
- `git-delete-branch`

These helpers are optimized for frequent interactive terminal use. Startup must stay fast and predictable.

## Commands

### `git-quick-push`

Behavior:

- Runs in the current Git repository.
- Stages all changes with `git add -A`.
- Commits staged content when there is anything to commit.
- Pushes the current branch.
- If the current branch has no upstream and `origin` exists, publishes with `git push -u origin <branch>`.
- If there is no commit content, it still tries to push or publish the current branch.

Commit message behavior:

- Default mode does not call AI.
- `-m "message"` or a positional message uses the provided commit subject.
- `-a` / `--ai` asks Codex to generate a Conventional Commit subject.
- The AI model defaults to `gpt-5.3-codex-spark`.
- AI generation is best-effort; if it fails, the script falls back to the local deterministic message generator.

### `git-create-branch`

Behavior:

- Lists current remote-tracking branches before prompting for the new branch name.
- Prompts with `请输入新分支名:`.
- Creates the new branch from the current branch.
- Moves all uncommitted changes into the new branch by delegating commit and push behavior to `git quick-push`.
- Supports the same commit message options as `git-quick-push`, including `-m` and `-a`.

Branch name behavior:

- User input is trimmed and slugified.
- Spaces and unsupported characters become `-`.
- Path separators are preserved after each segment is slugified.
- No branch type prefix is added automatically. For example, input `dev` creates `dev`, not `feature/dev`.

Remote branch list behavior:

- The list comes from local remote-tracking refs, equivalent in intent to `git branch -r`.
- `origin/HEAD` is omitted.
- If the list is stale or incomplete, run `git fetch --prune` manually before invoking the helper.
- The helper must not call `git ls-remote` or perform another network request just to show the list or pre-check the name.

Publish boundary:

- Startup and prompting must not depend on network.
- Final publish still uses `git push -u origin <branch>` when the branch has no upstream. That network cost is expected because publishing is part of the command contract.

### `git-delete-branch`

Behavior:

- Without arguments, shows an interactive selector.
- The selector must include local branches and local remote-tracking branches under `origin/`.
- Current remote branch entries such as `origin/feature/dev` must remain visible.
- The current local branch must not be offered as a local delete target.
- Protected branches such as `main`, `master`, and `develop` must not be offered in the selector and must be refused when passed directly.
- Selecting `origin/<branch>` deletes only the remote branch.
- Selecting `<branch>` deletes the local branch and deletes the matching remote branch when it exists.

Interactive behavior:

- Support arrow keys, `j` / `k`, Enter, and `q`.
- Treat both LF and CR Enter input as confirmation.
- Provide a non-TTY fallback that lists candidates and accepts typed input.

Performance rule:

- Candidate collection must use local refs only.
- Do not call `git ls-remote` while opening the selector.

## Implementation Lessons

- Interactive Git helpers must not do hidden remote preflight checks before the user can act. Network probes such as `git ls-remote` make simple prompts feel frozen when the remote is slow.
- Showing remote branches and checking whether a known remote branch exists should use local refs under `refs/remotes/`.
- When exact freshness is required, make the user-visible action explicit: `git fetch --prune`.
- Remote publish and remote delete are allowed to be slow because they are the requested operation. Listing, prompt rendering, and local validation are not allowed to be slow because of network.
- Tests should include wrappers that fail if interactive list/setup code calls `git ls-remote`.
- Terminal Enter handling must account for carriage return (`\r`) as well as newline (`\n`), especially for raw-mode selectors.

## Verification

Relevant checks:

```bash
bash scripts/test_git_quick_push.sh
bash scripts/test_git_create_branch.sh
bash scripts/test_git_delete_branch.sh
bash -n git-quick-push git-create-branch git-delete-branch
rg -n "ls-remote" git-create-branch git-delete-branch
```

The final `rg` command should return no matches in production helper scripts.
