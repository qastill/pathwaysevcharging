# PhD Monash — native GeoSPKLU section

Open `/#tab=phd` in the existing dashboard. PhD Monash contains an overview, concept map, eight-week research plan, literature, methods and data, existing analysis links, weekly progress and Obsidian notes. The old `/phd/` URL redirects to this menu.

All new interface text is English. The imported collection contains 94 English note guides, including 43 literature summaries with the main idea and use in this PhD. Original Obsidian text remains available as a Markdown download. Guides are concise syntheses rather than complete translations. The snapshot date is 28 September 2026; there is no automatic Obsidian sync.

Four original SVG illustrations explain usable access, dependence on public charging, the combination of evidence, and Gini versus the concentration index. Numeric examples are explicitly hypothetical.

The PhD navigation group also contains the existing Spatial Equity, Equity & Equality, Equity Map, Socio-Economic and Perception modules. These modules retain their original analyses and content. Existing tab URLs remain valid.

## Weekly progress

Entries contain the week, research question, status, target completion, target, results, evidence, blockers, next steps and supervision notes. Entries and work-package checkboxes use localStorage key `pathways.phd.monash.v1`. They stay in this browser and site origin; use JSON export/import to back up or transfer them. Markdown export supports supervision notes. Previous backups using `Lintas RQ` migrate to the English label `All RQs`.

No sample progress is loaded. Completion refers to the week's target or the eight work packages, not the whole PhD. The work plan is proposed, not an official Monash milestone schedule.

## Integration

`section.html` is injected directly into the dashboard. CSS is scoped to `.phd-workspace`; JavaScript is isolated in a closure and uses prefixed element IDs. There is no iframe or second website. Run `node phd/inject.cjs` after dashboard generation; the existing build does this before copying static files. Repeated injection is safe.

## Literature sources

Summaries use the imported research notes. Thin proposal-only entries were supplemented from publisher abstracts/pages for Asensio (2020), Karner, Pereira & Farber (2025; online 2024), Sheldon (2022), Yu (2025), Zheng (2024), and the Welch & Widita (2019) abstract. The English guides link to the original sources. Research-use paragraphs describe proposed applications to this PhD, not additional findings of those papers.
