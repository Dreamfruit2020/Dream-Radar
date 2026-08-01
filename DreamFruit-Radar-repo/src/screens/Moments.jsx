import { motion } from "framer-motion";
import { MOMENTS } from "../data/matrix.js";
import { ScreenHeader, rise } from "../components/UI.jsx";

export default function Moments({ config, update }) {
  const toggle = (id) =>
    update((c) => ({
      moments: c.moments.includes(id)
        ? c.moments.filter((m) => m !== id)
        : [...c.moments, id],
    }));

  return (
    <div>
      <ScreenHeader
        overline="04 · Performance Moments"
        title="Where does Dream integrate into your schedule?"
        sub="Select the moments in the athletic day where formulas will deploy. Multiple selections build a full-day system."
      />

      {/* timeline rail */}
      <div className="relative">
        <div className="absolute left-6 top-0 h-full w-px bg-white/10 md:left-0 md:top-[74px] md:h-px md:w-full" />

        <div className="grid gap-4 md:grid-cols-6 md:gap-3">
          {MOMENTS.map((m, i) => {
            const active = config.moments.includes(m.id);
            return (
              <motion.button
                key={m.id}
                variants={rise}
                custom={3 + i}
                initial="hidden"
                animate="show"
                whileHover={{ y: -5 }}
                whileTap={{ scale: 0.96 }}
                onClick={() => toggle(m.id)}
                className="relative pl-14 text-left md:pl-0 md:pt-[104px] md:text-center"
              >
                {/* node on the rail */}
                <span
                  className="absolute left-6 top-7 z-10 -translate-x-1/2 md:left-1/2 md:top-[74px] md:-translate-y-1/2"
                >
                  <span
                    className="block h-3.5 w-3.5 rounded-full border-2 transition-all duration-300"
                    style={{
                      borderColor: active ? m.color : "rgba(255,255,255,0.25)",
                      background: active ? m.color : "#0a0c12",
                      boxShadow: active ? `0 0 18px ${m.color}` : "none",
                    }}
                  />
                </span>

                {/* time stamp */}
                <span
                  className="absolute left-12 top-1 hidden text-[10px] font-semibold tracking-[0.2em] text-white/30 md:left-1/2 md:top-[46px] md:block md:-translate-x-1/2"
                >
                  {m.time}
                </span>

                <span
                  className="glass block rounded-2xl p-4 transition-shadow md:mt-6 md:min-h-[150px]"
                  style={{
                    borderColor: active ? `${m.color}99` : undefined,
                    boxShadow: active ? `0 0 30px ${m.color}33, inset 0 0 22px ${m.color}11` : "none",
                  }}
                >
                  <span className="block text-2xl">{m.icon}</span>
                  <span className="mt-2 block text-[13px] font-semibold text-white">{m.label}</span>
                  <span
                    className="mt-0.5 block text-[10px] font-bold uppercase tracking-[0.22em]"
                    style={{ color: active ? m.color : "rgba(255,255,255,0.35)" }}
                  >
                    {m.tag}
                  </span>
                  <span className="mt-2 hidden text-[11px] leading-snug text-white/40 md:block">{m.desc}</span>
                </span>
              </motion.button>
            );
          })}
        </div>
      </div>

      <motion.div
        variants={rise}
        custom={10}
        initial="hidden"
        animate="show"
        className="mt-10 text-center text-[12px] uppercase tracking-[0.24em] text-white/30"
      >
        {config.moments.length} of {MOMENTS.length} moments in your system
      </motion.div>
    </div>
  );
}
