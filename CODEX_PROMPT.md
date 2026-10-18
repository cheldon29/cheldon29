# Prompt to paste into Codex

You are deploying a small static site with one serverless function to Cloudflare Pages and attaching the domain `cheldon.fr`.

Repository: `cheldon29/cheldon29`, branch `claude/monetisation-flexible-txnaab`. The site lives in the `site/` folder
(`index.html`, `privacy.html`, `_headers`, `wrangler.toml`, `functions/api/pilot.js`). Do not redesign it.

## Tasks
1. Check out the branch. Authenticate Wrangler (`npx wrangler login`, or use `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID` if I provide them). Never print or commit secrets.
2. Create the KV namespace: `npx wrangler kv namespace create PILOTS`. Put the returned id into `site/wrangler.toml` (replace `REPLACE_WITH_KV_NAMESPACE_ID`). Commit that one change.
3. Create the Pages project: `npx wrangler pages project create cheldon-site --production-branch main`, then deploy from `site/` with `npx wrangler pages deploy site --project-name cheldon-site`.
4. Make sure the `PILOTS` KV binding is attached to the Pages project (production and preview) — Pages bindings are configured in the dashboard/API, not only in the toml; verify and fix if needed.
5. Attach the custom domain `cheldon.fr` (and `www.cheldon.fr` redirecting to the apex) to the Pages project. The zone is already on my Cloudflare account, so DNS records are created automatically; confirm SSL is Active.
6. Verify with curl:
   - `https://cheldon.fr/` returns 200 and the security headers from `_headers`.
   - `POST https://cheldon.fr/api/pilot` with `{"email":"test@example.com","consent":true,"company":"smoke test"}` returns `{"ok":true}`, and the entry then appears in KV (`npx wrangler kv key list --binding PILOTS`). Delete the smoke-test entry afterwards.
   - A request without consent returns 400.
7. Optional, only if I confirm: add a Cloudflare Email Routing address (e.g. `contact@cheldon.fr`) forwarding to my inbox, and tell me to put it into `site/privacy.html`.

## Constraints
- Do not enable analytics, cookies, or third-party scripts (the privacy notice says none are used).
- Do not change pricing, claims, or copy. Do not add testimonials or accuracy figures.
- Do not touch other DNS records or other zones/projects on the account.
- Report back: the deployed URLs, what you verified, and anything you could not do.

## Left for the human (do not invent these)
- Fill the placeholders in `site/privacy.html` (controller name/address/email, retention periods).
- Create the payment links (Stripe) later; the page currently routes all buttons to the application form.
