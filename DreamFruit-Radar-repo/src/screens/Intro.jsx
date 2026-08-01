import { motion } from "framer-motion";
import Bottle from "../components/Bottle.jsx";
import { Overline, PrimaryButton, rise } from "../components/UI.jsx";

const STATS = [
  { label: "Readiness", value: "94", accent: "#e02875", pos: "left-0 top-10" },
  { label: "Hydration", value: "+12%", accent: "#c8e63d", pos: "right-0 top-32" },
  { label: "Recovery Index", value: "8.6", accent: "#8b5cf6", pos: "left-4 bottom-16" },
];

export default function Intro({ next }) {
  return (
    <div className="flex min-h-[82vh] flex-col items-center gap-14 pt-10 md:flex-row md:gap-6 md:pt-4">
      {/* Copy */}
      <div className="max-w-xl flex-1 text-center md:text-left">
        <motion.div variants={rise} custom={0} initial="hidden" animate="show">
          <Overline color="#c8e63d">Dreamfruit · Powering Up Elite Athletes Through Nature</Overline>
        </motion.div>

        <motion.h1
          variants={rise}
          custom={1}
          initial="hidden"
          animate="show"
          className="font-display mt-6 text-[30px] leading-[1.14] text-white md:text-[46px] md:leading-[1.1]"
        >
          Build Your Club's
          <br />
          <span className="text-shimmer">Performance Matrix</span>
        </motion.h1>

        <motion.p
          variants={rise}
          custom={2}
          initial="hidden"
          animate="show"
          className="mx-auto mt-6 max-w-md text-[16px] leading-relaxed text-white/50 md:mx-0"
        >
          Personalised functional nutrition, engineered around your athletes.
        </motion.p>

        <motion.div variants={rise} custom={3} initial="hidden" animate="show" className="mt-10">
          <PrimaryButton onClick={next}>Open Your Performance Brief →</PrimaryButton>
        </motion.div>

        <motion.div
          variants={rise}
          custom={4}
          initial="hidden"
          animate="show"
          className="mt-12 flex items-center justify-center gap-7 text-[11px] font-medium uppercase tracking-[0.24em] text-white/30 md:justify-start"
        >
          <span>Natural</span>
          <span className="h-1 w-1 rounded-full bg-white/25" />
          <span>Personalised</span>
          <span className="h-1 w-1 rounded-full bg-white/25" />
          <span>Engineered</span>
        </motion.div>
      </div>

      {/* Bottle + telemetry */}
      <motion.div
        initial={{ opacity: 0, scale: 0.92 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 1, ease: [0.22, 1, 0.36, 1], delay: 0.15 }}
        className="relative w-[300px] md:w-[400px]"
      >
        <div className="floaty">
          <Bottle
            className="w-full"
            layers={[
              { color: "#e02875", intensity: 2 },
              { color: "#c8e63d", intensity: 2 },
              { color: "#8b5cf6", intensity: 1 },
            ]}
          />
        </div>

        {/* floating stat chips */}
        {STATS.map((s, i) => (
          <motion.div
            key={s.label}
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 + i * 0.2, duration: 0.6 }}
            className={`glass absolute ${s.pos} rounded-2xl px-4 py-3 ${i === 1 ? "floaty-slow" : "floaty"}`}
          >
            <div className="text-[9px] font-semibold uppercase tracking-[0.22em] text-white/40">{s.label}</div>
            <div className="mt-0.5 text-lg font-semibold" style={{ color: s.accent }}>
              {s.value}
            </div>
          </motion.div>
        ))}

        {/* telemetry sparkline */}
        <motion.svg
          viewBox="0 0 200 46"
          className="absolute -bottom-6 right-0 w-44"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.1 }}
        >
          <motion.path
            d="M2 38 L28 30 L52 34 L76 18 L102 24 L128 8 L156 14 L198 4"
            stroke="#c8e63d"
            strokeWidth="1.6"
            fill="none"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 2, ease: "easeInOut", delay: 1.2 }}
          />
          <circle cx="198" cy="4" r="3" fill="#c8e63d" className="pulse-glow" />
        </motion.svg>
      </motion.div>
    </div>
  );
}
