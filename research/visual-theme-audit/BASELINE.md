# Visual Theme Audit Baseline

- Started: 2026-08-26
- Git commit: `69f7b51c384ed2030c79e55dc3e7d339143c826b`
- Catalog source: `COMMERCIAL_THEMES` in `sites/lib/templates/index.js`
- Commercial theme count: **58**
- Production/deploy/push: forbidden for this audit

The worktree was already heavily modified before this audit. In particular,
most theme CSS modules and the chooser/preview/site routes were dirty. Those
changes are treated as the visual baseline and are not reverted. The first pass
is screenshot/measurement-only. A dirty shared/theme file is not edited unless
ownership is clear; otherwise the confirmed defect is reported as a conflict.

The complete starting `git status --short` is captured in
`worktree-start.txt` by the audit runner.
