<!-- Context: project-intelligence/nav | Priority: high | Version: 1.1 | Updated: 2026-06-19 -->

# Project Intelligence

> Start here for quick project understanding. These files bridge business and technical domains.

**Last Updated**: 2026-06-19

## Structure

```
.opencode/context/project-intelligence/
├── navigation.md              # This file - quick overview
├── technical-domain.md        # Tech stack, architecture, patterns (populated)
├── business-domain.md         # Business context, goals, roadmap (populated)
├── business-tech-bridge.md    # Business needs → technical solutions (populated)
├── decisions-log.md           # Major decisions with rationale (populated)
└── living-notes.md            # Active issues, debt, open questions (populated)
```

## Quick Routes

| What You Need | File | Description |
|---------------|------|-------------|
| Tech stack & patterns | `technical-domain.md` | FastAPI + Vue + MongoDB, code patterns, naming |
| Business context | `business-domain.md` | Project identity, goals, roadmap |
| Business → Tech mapping | `business-tech-bridge.md` | How features map to implementation |
| Decision rationale | `decisions-log.md` | Why key decisions were made |
| Current state & debt | `living-notes.md` | Active issues, open questions, lessons |
| All of the above | Read all files | Complete project intelligence |

## Usage

**New Developer / Agent**:
1. Start with `technical-domain.md` for the tech stack and patterns
2. Read `business-domain.md` for project context
3. Follow onboarding checklist in `living-notes.md`

**Quick Reference**:
- Backend patterns → `technical-domain.md` (Code Patterns section)
- Frontend patterns → `technical-domain.md` (Component Pattern section)
- API conventions → `technical-domain.md` (Naming Conventions section)
- Architecture decisions → `decisions-log.md`

## Integration

This folder is referenced from:
- `.opencode/context/core/standards/project-intelligence.md` (standards and patterns)
- `.opencode/command/add-context.md` (interactive wizard for updating)

See `.opencode/context/core/context-system.md` for the broader context architecture.

## Maintenance

Keep this folder current:
- Update when tech stack changes → `technical-domain.md`
- Document decisions as they're made → `decisions-log.md`
- Review `living-notes.md` regularly for active issues
- Run `/add-context --update` to guide updates

**Management Guide**: See `.opencode/context/core/standards/project-intelligence-management.md` for complete lifecycle management.
