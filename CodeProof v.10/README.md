# CodeProof v.10

Contains 8 local and 11 remote branch snapshots (19 folders). Remote tips were checked against GitHub before export.

Each branch folder contains the exact committed files at the SHA below. Local and remote copies are kept separately, including when they share a name or commit. origin/HEAD is a pointer to main and is not a separate branch.

These folders are source snapshots without .git directories. CodeProof-all-branches.bundle preserves Git history and references for recovery. BRANCH-MANIFEST.json records every file and its verified Git blob; BRANCH-INDEX.csv is a spreadsheet-friendly index.

Uncommitted files, ignored build outputs, local environment files, and installed dependencies are not included. Tracked files and tracked release packages are retained. No branch was merged, no application was compiled, and the original checkout was not changed.

| Location | Branch | Commit | Files |
|---|---|---|---:|
| [local](branches/local/codex/fix-ai-setup/) | codex/fix-ai-setup | 6040f8e5416d75481b37e2a52fae0928c3ca9661 | 243 |
| [local](branches/local/codex/fix-signing-secret-redaction/) | codex/fix-signing-secret-redaction | 911d45cc267d8972dd7b65d6cf260bd6e7a779db | 173 |
| [local](branches/local/codex/mvp-release-completion/) | codex/mvp-release-completion | 77786b4c23b6abcf000120e43c78230500c6f01d | 274 |
| [local](branches/local/codex/release-audit-p06-p15/) | codex/release-audit-p06-p15 | 911d45cc267d8972dd7b65d6cf260bd6e7a779db | 173 |
| [local](branches/local/feature/backend-integration/) | feature/backend-integration | 2874de18cfa1ed9fabbf04fa4f3b9af694e895a4 | 133 |
| [local](branches/local/feature/flutter-desktop/) | feature/flutter-desktop | c3a61e47a9a6e64472a8bf5ed26f9e1b001622ec | 115 |
| [local](branches/local/feature/flutter-desktop-v2/) | feature/flutter-desktop-v2 | e8ebf7c657db5379b98a384c947250e8096499db | 88 |
| [local](branches/local/test/mvp-integration/) | test/mvp-integration | 911d45cc267d8972dd7b65d6cf260bd6e7a779db | 173 |
| [remote](branches/remote/origin/codex/fix-ai-setup/) | origin/codex/fix-ai-setup | 6040f8e5416d75481b37e2a52fae0928c3ca9661 | 243 |
| [remote](branches/remote/origin/feature/ai-analysis-engine/) | origin/feature/ai-analysis-engine | ea9bdd5b6df690df93ae82d7e47a0cdebb3f1700 | 43 |
| [remote](branches/remote/origin/feature/ai-coaching-contract/) | origin/feature/ai-coaching-contract | 7fa4dacb84df4d9fde0dfa4fff130229e389fe0b | 47 |
| [remote](branches/remote/origin/feature/ai-coaching-engine/) | origin/feature/ai-coaching-engine | 0af2bc29b8802f9bc8b3536ae83eb50be99d7e49 | 44 |
| [remote](branches/remote/origin/feature/ai-guardian-contract/) | origin/feature/ai-guardian-contract | ec78486e4a292093a1087618171bf94d0a786e6c | 42 |
| [remote](branches/remote/origin/feature/ai-patch-generator/) | origin/feature/ai-patch-generator | 6efa548ab78a2b93075a395b777b2fe30206f403 | 48 |
| [remote](branches/remote/origin/feature/backend-integration/) | origin/feature/backend-integration | 2874de18cfa1ed9fabbf04fa4f3b9af694e895a4 | 133 |
| [remote](branches/remote/origin/feature/flutter-desktop/) | origin/feature/flutter-desktop | c8dfd9f4e1309ad96507d4bfe3fd77e2355fbd18 | 81 |
| [remote](branches/remote/origin/feature/flutter-desktop-v2/) | origin/feature/flutter-desktop-v2 | e8ebf7c657db5379b98a384c947250e8096499db | 88 |
| [remote](branches/remote/origin/main/) | origin/main | 77786b4c23b6abcf000120e43c78230500c6f01d | 274 |
| [remote](branches/remote/origin/master/) | origin/master | c6114639d6c5dd43ae4db5e4be6cfb9b753b9c97 | 93 |

## Restore an editable repository

From this folder, run:

```powershell
git init recovered
git -C recovered fetch "../CodeProof-all-branches.bundle" "refs/heads/*:refs/heads/*" "refs/remotes/origin/*:refs/remotes/origin/*"
git -C recovered switch -c main refs/remotes/origin/main
```

Each branch retains its own README and dependency requirements. Consult the branch documentation before building or running it.
