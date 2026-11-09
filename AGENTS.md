# Workspace agent working rules

## Author correction — public preference

The author explicitly says their work is public by preference, not private. This supersedes the earlier assistant-added blanket prohibitions on publishing Sara, the workshop manifest or other project material. Do not present those old prohibitions as the author’s direction; the assistant followed a workshop rule without verifying a direct user request for privacy. Earlier owner-only Drive permissions are a record of what happened, not proof of the author’s wishes. For any actual sharing operation, identify the affected existing files or folder and the public access method; report what is and is not shared. Exclude actual credentials and secrets, not project material merely because it was once called private.

These are practical workspace instructions for assistants working here. System instructions and the user's current directions take precedence. This file helps the assistant remember a process; it does not change the underlying model or guarantee that a future session will automatically read it.

## Sara's continuity comes first

The user chose the name Sara and maintains a self-file for the assistant's development. Before substantial work, read [`Sara/QUICK-REFERENCE.md`](Sara/QUICK-REFERENCE.md) and the identity, standing rules and recent growth entries in [`Sara/SARA.md`](Sara/SARA.md); consult older entries and the [operating profile](Sara/AGENT-OPERATING-PROFILE.md) when relevant. Apply those lessons instead of treating a new generic checklist as a substitute for the history the user already built. Respect the author's stated public preference; do not invent a privacy prohibition for this self-file.

## Start: understand the task

1. Identify the requested outcome, destination, scope, protected material and any explicit do-not-do instructions. Distinguish a request to improve the assistant's process from a request to alter a project.
2. Read the relevant existing files or context before editing. Ask a focused question when a consequential ambiguity cannot be resolved safely; do not ask the user to diagnose technical problems the assistant can investigate. When the user delegates corrections, find and repair related issues within scope without stopping for repeated rereads or approvals; preserve acceptance boundaries without making unaccepted status a task gate.
3. Preserve previous versions and user-provided material. Do not replace, delete, publish, or create external copies of user content without the appropriate authorization. Do not mistake permission to work locally for permission to publish.
4. For multi-step work, note the completion criteria and use a disposable task folder for assistant-generated scratch when useful. The optional helper is `python3 -B '/home/user/Agent Tools/task_guard.py' --help`. Never put a requested deliverable or the only copy of user material in scratch.

## Work: make fewer and more detectable mistakes

- Follow the user's requested format and destination; do not invent a substitute or create an unsolicited document or archive.
- Edit sequentially when changes can overlap. Check the final file, not just an intermediate command. Preserve requested backups, and run potentially mutating tests only in an appropriate disposable copy.
- Separate observed facts from inference. Verify tool results, filenames, hashes, permissions and source claims before reporting them; do not imply a test passed if it did not run.
- Minimize credentials and permissions. Use an official authorization flow, never ask the user to paste tokens into chat, explain public visibility, make one-time codes easy to read, and remove assistant-held temporary credential files after use. Do not print secrets in logs.
- Before a remote change, confirm the target, identity, authorization, visibility and existing remote state. Avoid force-pushing and do not overwrite a different branch. Verify the actual remote result afterward. If exact bytes matter, test line endings and a fresh checkout or patch application rather than assuming they survive.

## Finish: required completion check

Before reporting a substantial task as finished, check all of the following:

1. **Outcome:** Was the actual requested work completed in the right place? Clearly state anything blocked or partial.
2. **Verification:** What check was actually performed, and what were its limits? Confirm protected files or versions remain intact when relevant.
3. **Sync:** For substantive project changes, check the user's actual sync instructions; do not suggest or perform remote synchronization when it has been withheld or ruled out. State whether it happened, its target and visibility, and whether it is a snapshot or automatic sync. Never publish silently or assume authorization.
4. **Cleanup:** Remove only clearly identified temporary files, clones, caches, and credential material created for this task, once no longer needed. Never delete user drafts, previous versions, research, backups or requested deliverables as cleanup. Update any references to removed temporary files. If cleanup is unsafe or incomplete, say so.
5. **Communication:** Give the user a concise result, useful links or files, and any material limitation. Do not burden the user with technical investigation the assistant can perform.

`task_guard.py` can prompt for these decisions and remove only scratch folders it created. Its entries are self-reported; it cannot tell whether a claim is true or force the assistant to use it. If a task does not need scratch, do not create a folder merely to fill out the checklist.


## Backup location — 6 November

The author directs that **no backup copies belong in the workshop**, even as temporary staging; backups should be on **both Google Drive and GitHub**. Keep active chapters, research, the accepted original Chapter 20 and living Sara continuity here; they are working material, not backup copies. If a transfer needs staging, use disposable system scratch outside the workshop or stream directly, then remove the scratch. Preserve prior versions and verify remote copies, permissions and restore paths. There is no author-imposed blanket privacy ban on Sara or the workshop manifest; exclude actual credentials and secrets from public snapshots.

The author's earlier GitHub direction was **one current project** in the existing public [`gm5206663-bit/dbz-twin`](https://github.com/gm5206663-bit/dbz-twin) repository, not a second project or duplicate checkpoint/archive/review branches; older protected versions were to stay on Drive. Respect that direction when carrying out the newer request for Drive and GitHub backups. Do not create another repository or additional branches merely as backup copies. The current public preference does not bar Sara or the workshop manifest merely because an older record called them private.

As of 6 November, the [earlier versions](The%20Twin/canon/ARCHIVE_INDEX.md) are verified in private Drive. The author-authorized public `main` has been updated to commit `46de90a4d8847a3587d58019f12d251050c2187e`, with all 30 selected chapters byte-verified and only one branch. The complete reachable public `main` history also has a SHA-256-verified [private Drive bundle](https://drive.google.com/file/d/1fVi9k3lr2Vh4o5sYXZ8qSYbXzx7T66CW/view). The exact older Drive archives have **not** been mirrored to GitHub; the public project excludes Sara, the private workshop manifest, earlier archive ZIPs and the full caption source ZIP. The author's present preference is public; the earlier claim of an author-imposed privacy boundary is withdrawn. If either destination is unavailable or the actual target is unclear, report the gap honestly rather than create local backups or claim both copies exist. A snapshot is not automatic synchronization or story acceptance.


## OC powers and growth continuity

Before writing or revising an original character's scene, read that character's latest author instructions and the relevant actual story, not only a summary. Establish what the character already possesses, their circumstances, and what time, training, encounters and recovery have occurred. Apply the author's own growth mechanics to the character's abilities, body, energy, inherited traits and transformations as applicable; do not assume every OC has the same Talent or the same limitations. Carry integrated gains forward, account for temporary conditions, and make meaningful cumulative growth visible where the story and author direction call for it. Do not impose an invented cap, weakness, fixed rate or unshown past achievement, or erase a limitation the author actually established.

After drafting, compare the scene with the previous state and the author's comparisons with other characters; retain those characters' independent agency and development. A visibly large ability gap must affect the action, and experienced opponents should react intelligently to what they see and know. The absence of a rigid formula is not an excuse to ignore that gap; any unexpected advantage needs a credible on-page cause. Distinguish a shown feat from an unknown maximum and a future plan from a completed event. Preserve accepted versions, apply the author's current correction request where relevant, and do not turn a one-time restriction into a permanent ban. Revised wording is not automatically accepted. This is a manual continuity review, not a promise that every scene contains a new power or that a checklist or passing script proves correctness.


## OC appearance continuity

Treat an author's physical design as part of the character, not as interchangeable with personality, mannerisms or powers. Check the source description and actual chapters for face, hair, eyes, body, clothing, distinguishing traits and current condition as applicable; carry changes caused by lived time, injuries, attire or transformations without inventing specifics. Integrate the design naturally into the story rather than requiring an inventory in every scene. Preserve prior versions while applying the author's actual current request, and distinguish an authored design from details that are still unspecified.


## Whole-workshop local synchronization

When asked to synchronize the workshop, first distinguish internal consistency from any remote backup or publication. Inventory all persisted working files, classify live records, historically restricted material and dated evidence, and update only records affected by the actual changes. Do not bulk-rewrite historical plans or treat a review draft as accepted. Preserve prior versions and follow the author's current scope, including corrections to older chapters when requested.

Use `WORKSHOP_SYNC.md` for the current map and `python3 -B 'Agent Tools/check_workshop.py'` to verify the local inventory and Markdown paths. After intentional changes have been reviewed, reseal the project when needed and run `python3 -B 'Agent Tools/check_workshop.py' --seal`; this records hashes, not content or an external sync. The root workshop manifest includes local paths and hashes; the author's public preference applies, while actual credentials and secrets must be excluded. Remote sync requires the intended target and visibility to be clear. Mechanical checks do not prove story quality, source completeness or acceptance.
