# /frontend-check

Audit all frontend files against `02-frontend-rules.md`.

## Checks

1. **Emoji scan** — search `src/components/` for any emoji characters in JSX, string literals, or comments
2. **Icon audit** — verify all icons use `@heroicons/react` or `react-icons`, no emoji icons
3. **aria-label** — find all icon-only buttons and confirm they have `aria-label`
4. **TypeScript** — check for `any` types, `@ts-ignore`, missing type annotations on props
5. **Inline styles** — check for `style={{ ... }}` usage
6. **Draft status** — verify email draft and MOM screens show a status badge

## Output

List each violation with file path and line reference. No violation = pass.
