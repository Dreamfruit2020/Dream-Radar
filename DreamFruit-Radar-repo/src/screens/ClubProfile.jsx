import { motion } from "framer-motion";
import { TEAMS, CONTEXTS } from "../data/matrix.js";
import { Overline, ScreenHeader, rise } from "../components/UI.jsx";

export default function ClubProfile({ config, update }) {
  return (
    <div>
      <ScreenHeader
        overline="01 · Club Context"
        title="Who are we optimising for?"
        sub="Set the squad and the conditions it faces. This frames everything the Biological Architect reviews."
      />

      {/* Club name */}
      <motion.div variants={rise} custom={3} initial="hidden" animate="show" className="mx-auto mb-14 max-w-xl">
        <Overline className="mb-3 text-center">Club Name</Overline>
        <input
          value={config.clubName}
          onChange={(e) => update({ clubName: e.target.value })}
          placeholder="e.g. Meridian FC"
          className="field w-full pb-3 text-center text-2xl font-medium tracking-tight text-white md:text-3xl"
        />
      </motion.div>

      {/* Team */}
      <Overline className="mb-4">Team</Overline>
      <div className="mb-14 grid grid-cols-2 gap-3 md:grid-cols-4 md:gap-4">
        {TEAMS.map((t, i) => {
          const active = config.team === t.id;
          return (
            <motion.button
              key={t.id}
              variants={rise}
              custom={4 + i}
              initial="hidden"
              animate="show"
              whileHover={{ y: -4 }}
              whileTap={{ scale: 0.97 }}
              onClick={() => update({ team: t.id })}
              className="glass rounded-2xl p-5 text-left transition-shadow"
              style={{
                borderColor: active ? "rgba(224,40,117,0.6)" : undefined,
                boxShadow: active ? "0 0 34px rgba(224,40,117,0.22), inset 0 0 24px rgba(224,40,117,0.06)" : "none",
              }}
            >
              <div className="mb-3 flex items-center justify-between">
                <span
                  className="inline-block h-2 w-2 rounded-full transition-colors"
                  style={{ background: active ? "#e02875" : "rgba(255,255,255,0.18)" }}
                />
                {active && <span className="text-[9px] font-bold uppercase tracking-[0.2em] text-[#e02875]">Selected</span>}
              </div>
              <div className="text-[15px] font-semibold text-white">{t.label}</div>
              <div className="mt-1 text-[12px] text-white/40">{t.sub}</div>
            </motion.button>
          );
        })}
      </div>

      {/* Season context */}
      <Overline className="mb-1">Season Context</Overline>
      <p className="mb-4 text-[13px] text-white/35">The conditions your squad actually faces. Select all that apply.</p>
      <div className="mb-14 flex flex-wrap gap-2.5">
        {CONTEXTS.map((ctx, i) => {
          const active = config.contexts.includes(ctx.id);
          return (
            <motion.button
              key={ctx.id}
              variants={rise}
              custom={8 + i}
              initial="hidden"
              animate="show"
              whileHover={{ y: -3 }}
              whileTap={{ scale: 0.96 }}
              onClick={() =>
                update((c) => ({
                  contexts: c.contexts.includes(ctx.id)
                    ? c.contexts.filter((x) => x !== ctx.id)
                    : [...c.contexts, ctx.id],
                }))
              }
              className="glass rounded-full px-5 py-3 text-[13px] font-medium transition-colors"
              style={{
                borderColor: active ? "rgba(255,209,102,0.55)" : undefined,
                color: active ? "#ffd166" : "rgba(255,255,255,0.6)",
                boxShadow: active ? "0 0 26px rgba(255,209,102,0.16)" : "none",
              }}
            >
              {ctx.icon} {ctx.label}
            </motion.button>
          );
        })}
      </div>
    </div>
  );
}
