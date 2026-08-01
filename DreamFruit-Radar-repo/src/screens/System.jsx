import { motion } from "framer-motion";
import {
  TEAMS,
  CONTEXTS,
  OBSERVATIONS,
  TIMINGS,
  SCOPES,
  CURRENT_USE,
  VALIDATORS,
  CONSTRAINTS,
  MOMENTS,
  PILLARS,
  PROGRAMME,
  indicatedFamilies,
  estimateBottlesPerWeek,
} from "../data/matrix.js";
import Bottle from "../components/Bottle.jsx";
import { Overline, PrimaryButton, GhostButton, rise } from "../components/UI.jsx";

const FAMILY_VARIANTS = { activate: "POWER UP", charge: "POWER BOOST", restore: "POWER DOWN" };

function SectionLabel({ n, children }) {
  return (
    <div className="mb-5 flex items-center gap-3">
      <span className="text-[11px] font-bold tracking-[0.3em] text-white/25">{n}</span>
      <Overline color="#e02875">{children}</Overline>
      <span className="h-px flex-1 bg-white/8" />
    </div>
  );
}

function Chip({ children, color = "rgba(255,255,255,0.6)", border = "rgba(255,255,255,0.12)", bg = "rgba(255,255,255,0.03)" }) {
  return (
    <span className="rounded-full px-4 py-2 text-[12px] font-medium" style={{ color, border: `1px solid ${border}`, background: bg }}>
      {children}
    </span>
  );
}

function Quote({ text }) {
  if (!text || !text.trim()) return null;
  return (
    <div className="mt-4 rounded-2xl border-l-2 border-white/20 bg-white/3 px-5 py-4 text-[13px] italic leading-relaxed text-white/60">
      “{text.trim()}”
    </div>
  );
}

/** The Confidential Performance Brief — the platform opens the conversation;
    the Biological Architect carries it forward. */
export default function System({ config, restart }) {
  const team = TEAMS.find((t) => t.id === config.team);
  const contexts = CONTEXTS.filter((c) => config.contexts.includes(c.id));
  const observations = OBSERVATIONS.filter((o) => config.observations.includes(o.id));
  const timings = TIMINGS.filter((t) => config.timings.includes(t.id));
  const scope = SCOPES.find((s) => s.id === config.scope);
  const currentUse = CURRENT_USE.filter((u) => config.currentUse.includes(u.id));
  const validator = VALIDATORS.find((v) => v.id === config.validator);
  const constraints = CONSTRAINTS.filter((k) => config.constraints.includes(k.id));
  const moments = MOMENTS.filter((m) => config.moments.includes(m.id));
  const families = indicatedFamilies(config);
  const weekly = estimateBottlesPerWeek(config);

  return (
    <div className="pb-10">
      {/* ── Reveal header ─────────────────────────────── */}
      <div className="mb-14 text-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
          className="mx-auto mb-7 flex h-16 w-16 items-center justify-center rounded-full"
          style={{
            background: "linear-gradient(135deg, rgba(224,40,117,0.18), rgba(200,230,61,0.14))",
            border: "1px solid rgba(255,255,255,0.14)",
            boxShadow: "0 0 60px rgba(224,40,117,0.3)",
          }}
        >
          <span className="text-2xl">✦</span>
        </motion.div>
        <motion.div variants={rise} custom={1} initial="hidden" animate="show">
          <Overline color="#c8e63d">Confidential · Prepared For Biological Architect Review</Overline>
        </motion.div>
        <motion.h2
          variants={rise}
          custom={2}
          initial="hidden"
          animate="show"
          className="font-display mt-4 text-[26px] leading-[1.16] text-white md:text-[42px] md:leading-[1.1]"
        >
          Your <span className="text-shimmer">Performance Brief</span>
        </motion.h2>
        <motion.p variants={rise} custom={3} initial="hidden" animate="show" className="mt-4 text-[15px] text-white/45">
          {config.clubName || "Your club"} has opened the conversation. Dreamfruit takes it from here.
        </motion.p>
      </div>

      {/* ── 1 · Club context ──────────────────────────── */}
      <motion.section variants={rise} custom={4} initial="hidden" animate="show" className="mb-14">
        <SectionLabel n="01">Club Context</SectionLabel>
        <div className="glass overflow-hidden rounded-3xl">
          <div className="grid divide-y divide-white/6 md:grid-cols-3 md:divide-x md:divide-y-0">
            {[
              { label: "Club", value: config.clubName || "Your Club", sub: team ? team.label : "" },
              { label: "Programme", value: PROGRAMME.name, sub: "Discover → Optimise" },
              { label: "Status", value: "Ready For BA Review", sub: "Confidential — club & Dreamfruit only", live: true },
            ].map((r) => (
              <div key={r.label} className="p-6 md:p-7">
                <div className="text-[10px] font-semibold uppercase tracking-[0.24em] text-white/35">{r.label}</div>
                <div className="mt-2 flex items-center gap-2.5 text-[18px] font-semibold text-white">
                  {r.live && (
                    <span className="relative flex h-2.5 w-2.5">
                      <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[#c8e63d] opacity-60" />
                      <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-[#c8e63d]" />
                    </span>
                  )}
                  {r.value}
                </div>
                {r.sub && <div className="mt-1 text-[12px] text-white/35">{r.sub}</div>}
              </div>
            ))}
          </div>
          <div className="border-t border-white/6 p-6 md:p-7">
            <div className="mb-3 text-[10px] font-semibold uppercase tracking-[0.24em] text-white/35">Season Context</div>
            <div className="flex flex-wrap gap-2">
              {contexts.map((c) => (
                <Chip key={c.id} color="#ffd166" border="rgba(255,209,102,0.35)" bg="rgba(255,209,102,0.07)">
                  {c.icon} {c.label}
                </Chip>
              ))}
            </div>
          </div>
        </div>
      </motion.section>

      {/* ── 2 · Observations ──────────────────────────── */}
      <motion.section variants={rise} custom={5} initial="hidden" animate="show" className="mb-14">
        <SectionLabel n="02">What The Club Is Observing</SectionLabel>
        <div className="glass rounded-3xl p-7">
          <div className="grid gap-3 sm:grid-cols-2">
            {observations.map((o, i) => (
              <motion.div
                key={o.id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.4 + i * 0.06 }}
                className="flex items-start gap-3.5 rounded-2xl border border-white/6 bg-white/3 px-5 py-4"
              >
                <span className="text-xl">{o.icon}</span>
                <span>
                  <span className="block text-[13px] font-semibold text-white">{o.label}</span>
                  <span className="mt-0.5 block text-[11px] text-white/40">{o.desc}</span>
                </span>
              </motion.div>
            ))}
          </div>

          <div className="mt-6 grid gap-5 md:grid-cols-2">
            <div>
              <div className="mb-2.5 text-[10px] font-semibold uppercase tracking-[0.24em] text-white/35">Appears</div>
              <div className="flex flex-wrap gap-2">
                {timings.map((t) => (
                  <Chip key={t.id} color="#c8e63d" border="rgba(200,230,61,0.35)" bg="rgba(200,230,61,0.06)">
                    {t.label}
                  </Chip>
                ))}
              </div>
            </div>
            <div>
              <div className="mb-2.5 text-[10px] font-semibold uppercase tracking-[0.24em] text-white/35">Affects</div>
              {scope && (
                <Chip color="#a78bfa" border="rgba(139,92,246,0.4)" bg="rgba(139,92,246,0.08)">
                  {scope.label}
                </Chip>
              )}
            </div>
          </div>

          <Quote text={config.obsNotes} />
        </div>
      </motion.section>

      {/* ── 3 · Current protocols ─────────────────────── */}
      <motion.section variants={rise} custom={6} initial="hidden" animate="show" className="mb-14">
        <SectionLabel n="03">Current Protocols & Requirements</SectionLabel>
        <div className="glass rounded-3xl p-7">
          <div className="grid gap-6 md:grid-cols-3">
            <div>
              <div className="mb-2.5 text-[10px] font-semibold uppercase tracking-[0.24em] text-white/35">In Use Today</div>
              <div className="flex flex-wrap gap-2">
                {currentUse.map((u) => (
                  <Chip key={u.id}>{u.label}</Chip>
                ))}
              </div>
            </div>
            <div>
              <div className="mb-2.5 text-[10px] font-semibold uppercase tracking-[0.24em] text-white/35">Validated By</div>
              {validator && (
                <Chip color="#4cc9f0" border="rgba(76,201,240,0.35)" bg="rgba(76,201,240,0.07)">
                  {validator.label}
                </Chip>
              )}
            </div>
            <div>
              <div className="mb-2.5 text-[10px] font-semibold uppercase tracking-[0.24em] text-white/35">Must Fit</div>
              <div className="flex flex-wrap gap-2">
                {constraints.length ? (
                  constraints.map((k) => (
                    <Chip key={k.id} color="#ffd166" border="rgba(255,209,102,0.35)" bg="rgba(255,209,102,0.06)">
                      {k.label}
                    </Chip>
                  ))
                ) : (
                  <span className="text-[12px] text-white/35">No constraints declared</span>
                )}
              </div>
            </div>
          </div>
          <Quote text={config.protocolNotes} />
        </div>
      </motion.section>

      {/* ── 4 · Deployment moments ────────────────────── */}
      <motion.section variants={rise} custom={7} initial="hidden" animate="show" className="mb-14">
        <SectionLabel n="04">Where Dream Can Deploy</SectionLabel>
        <div className="flex flex-wrap gap-2.5">
          {moments.map((m) => (
            <Chip key={m.id} color={m.color} border={`${m.color}55`} bg={`${m.color}0f`}>
              {m.icon} {m.label} · {m.tag}
            </Chip>
          ))}
        </div>
      </motion.section>

      {/* ── 5 · Architectural directions ──────────────── */}
      <motion.section variants={rise} custom={8} initial="hidden" animate="show" className="mb-14">
        <SectionLabel n="05">Architectural Directions</SectionLabel>
        <p className="mb-6 -mt-1 text-[13px] leading-relaxed text-white/40">
          Indicated by your observations — revealed by Dreamfruit, refined with your Biological Architect. Not a
          choice the club needs to make.
        </p>
        <div className="grid gap-5 md:grid-cols-3">
          {PILLARS.map((p, i) => {
            const strength = families[p.id] || 0;
            const indicated = strength > 0;
            return (
              <motion.div
                key={p.id}
                initial={{ opacity: 0, y: 26 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 + i * 0.15, duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
                className="glass relative overflow-hidden rounded-3xl p-6 text-center"
                style={{
                  opacity: indicated ? 1 : 0.55,
                  boxShadow: indicated ? `inset 0 0 40px ${p.color}0e, 0 0 30px ${p.color}14` : "none",
                  borderColor: indicated ? `${p.color}55` : undefined,
                }}
              >
                <span
                  className="absolute inset-x-0 top-0 h-[3px]"
                  style={{ background: `linear-gradient(90deg, transparent, ${p.color}, transparent)`, opacity: indicated ? 1 : 0.25 }}
                />
                {indicated && (
                  <span
                    className="absolute right-4 top-4 rounded-full px-2.5 py-1 text-[9px] font-bold uppercase tracking-[0.16em]"
                    style={{ background: `${p.color}1c`, color: p.color, border: `1px solid ${p.color}50` }}
                  >
                    Indicated
                  </span>
                )}
                <Bottle className="mx-auto -mb-2 -mt-4 w-36" color={p.color} color2={p.color2} variant={FAMILY_VARIANTS[p.id]} />
                <div className="text-[17px] font-bold tracking-[0.22em]" style={{ color: p.color }}>
                  {p.name}
                </div>
                <div className="mt-1.5 text-[12px] text-white/50">{p.purpose}</div>
                <div className="mt-4 flex flex-wrap justify-center gap-1.5">
                  {p.bases.map((b) => (
                    <span key={b} className="rounded-full border border-white/10 bg-white/4 px-2.5 py-1 text-[10px] text-white/55">
                      {b}
                    </span>
                  ))}
                </div>
              </motion.div>
            );
          })}
        </div>
      </motion.section>

      {/* ── 6 · Next steps ────────────────────────────── */}
      <motion.section variants={rise} custom={9} initial="hidden" animate="show" className="mb-14">
        <SectionLabel n="06">Next Steps</SectionLabel>
        <div className="grid gap-5 md:grid-cols-3">
          <div className="glass rounded-3xl p-6">
            <div className="mb-3 text-[13px] font-bold uppercase tracking-[0.16em] text-white">BA Discovery</div>
            <p className="text-[13px] leading-relaxed text-white/55">
              Your Biological Architect reviews this brief with your nutrition, medical and performance staff to
              reveal the underlying pattern.
            </p>
          </div>
          {PROGRAMME.months.map((m, i) => (
            <div key={m.title} className="glass rounded-3xl p-6">
              <div className="mb-3 text-[13px] font-bold uppercase tracking-[0.16em]" style={{ color: i === 0 ? "#e02875" : "#c8e63d" }}>
                {m.title}
              </div>
              <div className="space-y-2">
                {m.points.map((pt) => (
                  <div key={pt} className="flex items-center gap-2.5 text-[13px] text-white/60">
                    <span style={{ color: i === 0 ? "#e02875" : "#c8e63d" }}>✓</span> {pt}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
        <div className="mt-5 text-center text-[12px] uppercase tracking-[0.22em] text-white/30">
          Indicative scale · ~{weekly.toLocaleString()} bottles / week once protocols are live
        </div>
      </motion.section>

      {/* ── CTAs ──────────────────────────────────────── */}
      <motion.div
        variants={rise}
        custom={10}
        initial="hidden"
        animate="show"
        className="no-print flex flex-col items-center justify-center gap-4 pt-2 sm:flex-row"
      >
        <PrimaryButton onClick={() => window.print()}>Download Performance Brief PDF</PrimaryButton>
        <GhostButton
          onClick={() => {
            window.location.href =
              "mailto:performance@dream.example?subject=" +
              encodeURIComponent(`Performance Brief — ${config.clubName || "Club"} · BA Review`);
          }}
        >
          Send To Biological Architect
        </GhostButton>
      </motion.div>

      <motion.div variants={rise} custom={11} initial="hidden" animate="show" className="no-print mt-8 text-center">
        <button onClick={restart} className="text-[11px] uppercase tracking-[0.24em] text-white/30 transition-colors hover:text-white/60">
          Start A New Brief
        </button>
      </motion.div>
    </div>
  );
}
