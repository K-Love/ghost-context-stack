# Backstage Interactive - Redesign Plan

## Architecture
- **Framework**: Tailwind CSS (CDN for rapid prototyping)
- **Theme**: Deep Obsidian/Dark Mode
- **Navigation**: Sticky header with clean links: Agency, Studio, About, Contact.
- **Form**: Netlify Forms integration (contact@backstageinteractive.com)

## Clean URLs
- Will use Netlify "Pretty URLs" (Asset Optimization) or a `_redirects` file to ensure:
  - `/agency` -> `agency.html`
  - `/studio` -> `studio.html`
  - `/about` -> `about.html`
  - `/contact` -> `contact.html`

## Studio Portfolio Items
- **HerbCraft**: pSEO Herb Directory (Live)
- **GhostContext**: Risk-Aversion SaaS (Beta)
- **RE-VERB**: Developer CLI Pro (Dev)

## Agency Section
- Migration of existing client work from old `agency.html`.
