# PhD Monash workspace

Open `/phd/` for the full workspace, or `/#tab=phd` inside GeoSPKLU. The **PhD Monash** navigation group owns Spatial Equity, Ekuitas vs Kesetaraan, Peta Ekuitas, Socio-Economic, and Perception. Existing tab URLs remain valid.

## Contents

- Overview and the RQ1–RQ4 concept map, based on the newer Obsidian concept note.
- Eight work packages with editable completion checkpoints.
- Searchable literature and a reader for the imported research notes, including internal wiki links and Markdown download.
- Methods, data requirements, and links to the existing analysis modules.
- Weekly entries: target, achievement, evidence, blockers, next steps, supervision, status, and self-reported completion of that week's target.

`notes.json` is a dated snapshot of 94 selected research notes (43 literature notes) from Pathways-Vault, including the GeoSPKLU completion plan. It includes the research notes at the vault root, Exercises, Research Questions, Concepts, and Literature; gallery-only notes, videos, media binaries, and private supervision correspondence are excluded. Source paths and original draft content are retained. Original claims are not treated as verified findings; the interface labels them as working notes and highlights methodological cautions. No automatic sync with Obsidian is configured.

## Checkpoint storage

Entries and work-package checkboxes are stored under `pathways.phd.monash.v1` in this browser's localStorage. Data is **not shared across browsers, devices, or deployment origins**. Export JSON for backup or transfer between preview and production; import merges by week and asks before replacing existing weeks. Markdown export is available for supervision summaries. No sample progress is preloaded and no dissertation completion percentage is invented.

Local storage failures are reported without clearing the form. Imports are size/schema validated; user input and note HTML are escaped, and source links accept only HTTP(S). Deletion requires confirmation.

## Integration and reproduction

Run `node phd/inject.cjs` after generating `index.html`. The Vercel build runs it before copying the site to `public/`. The script is idempotent and leaves all analysis renderers/data intact.

For local preview, serve the repository through an HTTP server and open `/phd/`. No build or third-party JavaScript is required for the workspace. Web fonts have system font fallbacks.

The workspace's RQ numbering follows `29 Peta Konsep Penelitian SPKLU.md`. Older paper-library plans use a different numbering; this implementation does not rewrite those manuscripts or imply supervisor approval.
