// Cloudflare Pages Function: POST /api/pilot
// Stores pilot applications in the KV namespace bound as PILOTS.
const EMAIL = /^[^\s@]{1,64}@[^\s@]{1,190}\.[^\s@]{2,}$/;
const json = (body, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } });

export async function onRequestPost({ request, env }) {
  if (!env.PILOTS) return json({ error: "Service not configured." }, 503);
  let d;
  try { d = await request.json(); } catch { return json({ error: "Invalid request." }, 400); }

  if (d.website) return json({ ok: true }); // honeypot: pretend success to bots
  const email = String(d.email || "").trim().toLowerCase();
  if (!EMAIL.test(email)) return json({ error: "Please enter a valid email." }, 400);
  if (d.consent !== true) return json({ error: "Consent is required." }, 400);

  const ip = request.headers.get("cf-connecting-ip") || "unknown";
  const rlKey = `rl:${ip}`;
  const hits = parseInt((await env.PILOTS.get(rlKey)) || "0", 10);
  if (hits >= 5) return json({ error: "Too many attempts, try later." }, 429);
  await env.PILOTS.put(rlKey, String(hits + 1), { expirationTtl: 3600 });

  const rec = {
    email,
    company: String(d.company || "").slice(0, 120),
    volume: String(d.volume || "").slice(0, 40),
    note: String(d.note || "").slice(0, 500),
    at: new Date().toISOString(),
  };
  await env.PILOTS.put(`pilot:${rec.at}:${email}`, JSON.stringify(rec), { expirationTtl: 60 * 60 * 24 * 365 });
  return json({ ok: true });
}

export const onRequest = () => json({ error: "Method not allowed." }, 405);
