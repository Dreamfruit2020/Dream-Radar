import { motion } from "framer-motion";
import { CURRENT_USE, VALIDATORS, CONSTRAINTS } from "../data/matrix.js";
import { Overline, ScreenHeader, rise } from "../components/UI.jsx";

/** What's already in place — so Dream fits the club's reality,
    including validation and anti-doping requirements. */
export default function Protocols({ config, update }) {
  const toggleIn = (key, id) =>
    update((c) => ({
      [key]: c[key].includes(id) ? c[key].filter((x) => x !== id) : [...c[key], id],
    }));

  return (
    <div>
      <ScreenHeader
        overline="03 · Current Protocols"
        title="What's already in place?"
        sub="Dream integrates with your existing protocols — it doesn't ignore them. Nothing here is shared beyond your Biological Architect."
      />

      {/* In use today */}
      <Overline className="mb-4">In Use Before / During / After Sessions</Overline>
      <motion.div variants={rise} custom={3} initial="hidden" animate="show" className="mb-8 flex flex-wrap gap-2.5">
        {CURRENT_USE.map((u) => {
          const active = config.currentUse.includes(u.id);
          return (
            <button
              key={u.id}
              onClick={() => toggleIn("currentUse", u.id)}
              className="glass rounded-full px-5 py-3 text-[13px] font-medium transition-colors"
              style={{
                borderColor: active ? "rgba(224,40,117,0.55)" : undefined,
                color: active ? "#ff6aa5" : "rgba(255,255,255,0.6)",
                boxShadow: active ? "0 0 24px rgba(224,40,117,0.14)" : "none",
              }}
            >
              {u.label}
            </button>
          );
        })}
      </motion.div>

      <motion.div variants={rise} custom={4} initial="hidden" animate="show" className="mb-12">
        <textarea
          value={config.protocolNotes}
          onChange={(e) => update({ protocolNotes: e.target.value })}
          rows={3}
          placeholder="Optional — products, brands, timing or doses if known. e.g. 'Electrolyte mix at half-time, casein evenings, caffeine gum pre-match for some players…'"
          className="field-area w-full p-5 text-[14px] leading-relaxed text-white"
        />
      </motion.div>

      {/* Validation */}
      <Overline className="mb-4">Who Validates Nutrition At The Club?</Overline>
      <motion.div variants={rise} custom={5} initial="hidden" animate="show" className="mb-12 flex flex-wrap gap-2.5">
        {VALIDATORS.map((v) => {
          const active = config.validator === v.id;
          return (
            <button
              key={v.id}
              onClick={() => update({ validator: v.id })}
              className="glass rounded-full px-5 py-3 text-[13px] font-medium transition-colors"
              style={{
                borderColor: active ? "rgba(76,201,240,0.55)" : undefined,
                color: active ? "#4cc9f0" : "rgba(255,255,255,0.6)",
                boxShadow: active ? "0 0 24px rgba(76,201,240,0.14)" : "none",
              }}
            >
              {v.label}
            </button>
          );
        })}
      </motion.div>

      {/* Constraints */}
      <Overline className="mb-1">Requirements The Programme Must Fit</Overline>
      <p className="mb-4 text-[13px] text-white/35">Select all that apply — practical, dietary and anti-doping.</p>
      <motion.div variants={rise} custom={6} initial="hidden" animate="show" className="flex flex-wrap gap-2.5">
        {CONSTRAINTS.map((k) => {
          const active = config.constraints.includes(k.id);
          return (
            <button
              key={k.id}
              onClick={() => toggleIn("constraints", k.id)}
              className="glass rounded-full px-5 py-3 text-[13px] font-medium transition-colors"
              style={{
                borderColor: active ? "rgba(255,209,102,0.55)" : undefined,
                color: active ? "#ffd166" : "rgba(255,255,255,0.6)",
                boxShadow: active ? "0 0 24px rgba(255,209,102,0.14)" : "none",
              }}
            >
              {k.label}
            </button>
          );
        })}
      </motion.div>
    </div>
  );
}
