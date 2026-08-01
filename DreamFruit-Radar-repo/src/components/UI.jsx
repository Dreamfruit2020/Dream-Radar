import { motion } from "framer-motion";

/* Shared motion presets */
export const EASE = [0.22, 1, 0.36, 1];

export const screenVariants = {
  hidden: { opacity: 0, y: 28, filter: "blur(6px)" },
  show: { opacity: 1, y: 0, filter: "blur(0px)", transition: { duration: 0.65, ease: EASE } },
  exit: { opacity: 0, y: -20, filter: "blur(6px)", transition: { duration: 0.35, ease: "easeIn" } },
};

export const rise = {
  hidden: { opacity: 0, y: 22 },
  show: (i = 0) => ({
    opacity: 1,
    y: 0,
    transition: { delay: 0.05 * i, duration: 0.55, ease: EASE },
  }),
};

/* Simplified Dreamfruit dragonfruit mark — magenta fruit, lime spikes,
   dark maroon outline (vector echo of the brand logo). */
export function DreamfruitMark({ size = 26 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 48 48" fill="none">
      <g stroke="#2b0d16" strokeWidth="2.4" strokeLinejoin="round">
        <path d="M24 2c1.6 4.4 5 5.6 6.2 9.4L26 9.6l4.8 6.2-5-1.8 2 4.6" fill="#c8e63d" />
        <path d="M11 16c3.6-.4 5.8 1.6 7 4l-4.4 1.4M37 16c-3.6-.4-5.8 1.6-7 4l4.4 1.4" fill="#c8e63d" />
        <path d="M24 9c8.6 3.6 13 10.4 13 18a13 13 0 0 1-26 0c0-7.6 4.4-14.4 13-18Z" fill="#e02875" />
        <path d="M24 13.4c2 3 4.8 4.4 4.4 8l-4.4-2.2-4.4 2.2c-.4-3.6 2.4-5 4.4-8Z" fill="#c8e63d" strokeWidth="1.8" />
      </g>
    </svg>
  );
}

export function Overline({ children, color = "rgba(255,255,255,0.42)", className = "" }) {
  return (
    <div
      className={`text-[11px] font-semibold uppercase tracking-[0.3em] ${className}`}
      style={{ color }}
    >
      {children}
    </div>
  );
}

export function ScreenHeader({ overline, title, sub }) {
  return (
    <div className="mx-auto mb-10 max-w-3xl text-center md:mb-14">
      <motion.div variants={rise} custom={0} initial="hidden" animate="show">
        <Overline color="#e02875">{overline}</Overline>
      </motion.div>
      <motion.h2
        variants={rise}
        custom={1}
        initial="hidden"
        animate="show"
        className="font-display mt-4 text-[24px] leading-[1.16] text-white md:text-[36px] md:leading-[1.14]"
      >
        {title}
      </motion.h2>
      {sub && (
        <motion.p
          variants={rise}
          custom={2}
          initial="hidden"
          animate="show"
          className="mx-auto mt-4 max-w-xl text-[15px] leading-relaxed text-white/50"
        >
          {sub}
        </motion.p>
      )}
    </div>
  );
}

export function PrimaryButton({ children, onClick, disabled, className = "" }) {
  return (
    <motion.button
      whileHover={disabled ? {} : { scale: 1.03 }}
      whileTap={disabled ? {} : { scale: 0.97 }}
      onClick={onClick}
      disabled={disabled}
      className={`relative rounded-full px-8 py-4 text-[13px] font-semibold uppercase tracking-[0.22em] text-white transition-opacity ${
        disabled ? "cursor-not-allowed opacity-30" : ""
      } ${className}`}
      style={{
        background: "linear-gradient(120deg, #e02875, #ff4f9a)",
        boxShadow: disabled ? "none" : "0 0 42px rgba(224,40,117,0.38), inset 0 1px 0 rgba(255,255,255,0.25)",
      }}
    >
      {children}
    </motion.button>
  );
}

export function GhostButton({ children, onClick, className = "" }) {
  return (
    <motion.button
      whileHover={{ scale: 1.03 }}
      whileTap={{ scale: 0.97 }}
      onClick={onClick}
      className={`glass rounded-full px-7 py-4 text-[13px] font-semibold uppercase tracking-[0.22em] text-white/70 transition-colors hover:text-white ${className}`}
    >
      {children}
    </motion.button>
  );
}

/* Ambient backdrop — orbs + telemetry grid, shared by every screen */
export function Backdrop() {
  return (
    <div className="pointer-events-none fixed inset-0 z-0">
      <div className="grid-lines absolute inset-0" />
      <div
        className="absolute -left-40 -top-40 h-[560px] w-[560px] rounded-full opacity-[0.16] blur-[130px]"
        style={{ background: "#e02875" }}
      />
      <div
        className="absolute -bottom-48 -right-32 h-[520px] w-[520px] rounded-full opacity-[0.13] blur-[130px]"
        style={{ background: "#c8e63d" }}
      />
      <div
        className="absolute left-1/2 top-1/3 h-[420px] w-[420px] -translate-x-1/2 rounded-full opacity-[0.09] blur-[130px]"
        style={{ background: "#8b5cf6" }}
      />
      <div
        className="absolute inset-0"
        style={{ background: "radial-gradient(ellipse at 50% 120%, transparent 40%, rgba(3,4,8,0.9) 100%)" }}
      />
    </div>
  );
}
