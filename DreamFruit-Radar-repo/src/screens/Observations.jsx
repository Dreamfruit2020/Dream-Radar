import { motion } from "framer-motion";
import { OBSERVATIONS, TIMINGS, SCOPES } from "../data/matrix.js";
import { Overline, ScreenHeader, rise } from "../components/UI.jsx";

/** Observation-led intake — the club describes what it sees.
    Dreamfruit and the Biological Architect reveal the pattern. */
export default function Observations({ config, update }) {
  const toggleIn = (key, id) =>
    update((c) => ({
      [key]: c[key].includes(id) ? c[key].filter((x) => x !== id) : [...c[key], id],
    }));

  return (
    <div>
      <ScreenHeader
        overline="02 · Observations"
        title="What are you seeing?"
        sub="Describe what you observe — not what you think the cause is. Pattern analysis is our job."
      />

      {/* What is being observed */}
      <Overline className="mb-4">On The Pitch</Overline>
      <div className="mb-12 grid grid-cols-2 gap-3 md:grid-cols-4 md:gap-4">
        {OBSERVATIONS.map((o, i) => {
          const active = config.observations.includes(o.id);
          return (
            <motion.button
              key={o.id}
              variants={rise}
              custom={3 + i}
              initial="hidden"
              animate="show"
              whileHover={{ y: -4 }}
              whileTap={{ scale: 0.97 }}
              onClick={() => toggleIn("observations", o.id)}
              className="glass rounded-2xl p-5 text-left"
              style={{
                borderColor: active ? "rgba(224,40,117,0.6)" : undefined,
                boxShadow: active ? "0 0 30px rgba(224,40,117,0.2), inset 0 0 22px rgba(224,40,117,0.06)" : "none",
              }}
            >
              <div className="mb-2.5 text-2xl">{o.icon}</div>
              <div className="text-[13px] font-semibold leading-snug text-white">{o.label}</div>
              <div className="mt-1.5 text-[11px] leading-snug text-white/40">{o.desc}</div>
            </motion.button>
          );
        })}
      </div>

      {/* When it appears */}
      <Overline className="mb-4">When Does It Appear?</Overline>
      <motion.div variants={rise} custom={11} initial="hidden" animate="show" className="mb-12 flex flex-wrap gap-2.5">
        {TIMINGS.map((t) => {
          const active = config.timings.includes(t.id);
          return (
            <button
              key={t.id}
              onClick={() => toggleIn("timings", t.id)}
              className="glass rounded-full px-5 py-3 text-[13px] font-medium transition-colors"
              style={{
                borderColor: active ? "rgba(200,230,61,0.55)" : undefined,
                color: active ? "#c8e63d" : "rgba(255,255,255,0.6)",
                boxShadow: active ? "0 0 24px rgba(200,230,61,0.14)" : "none",
              }}
            >
              {t.label}
            </button>
          );
        })}
      </motion.div>

      {/* Who is affected */}
      <Overline className="mb-4">Who Is Affected?</Overline>
      <motion.div variants={rise} custom={12} initial="hidden" animate="show" className="mb-12 flex flex-wrap gap-2.5">
        {SCOPES.map((s) => {
          const active = config.scope === s.id;
          return (
            <button
              key={s.id}
              onClick={() => update({ scope: s.id })}
              className="glass rounded-full px-5 py-3 text-[13px] font-medium transition-colors"
              style={{
                borderColor: active ? "rgba(139,92,246,0.6)" : undefined,
                color: active ? "#a78bfa" : "rgba(255,255,255,0.6)",
                boxShadow: active ? "0 0 24px rgba(139,92,246,0.16)" : "none",
              }}
            >
              {s.label}
            </button>
          );
        })}
      </motion.div>

      {/* In their own words */}
      <Overline className="mb-3">In Your Own Words</Overline>
      <motion.div variants={rise} custom={13} initial="hidden" animate="show">
        <textarea
          value={config.obsNotes}
          onChange={(e) => update({ obsNotes: e.target.value })}
          rows={3}
          placeholder="Optional — anything the cards don't capture. e.g. 'Mainly after midweek away games, and it's worse for the U23s coming up…'"
          className="field-area w-full p-5 text-[14px] leading-relaxed text-white"
        />
      </motion.div>
    </div>
  );
}
