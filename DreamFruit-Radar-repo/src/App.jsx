import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Backdrop, screenVariants, DreamfruitMark } from "./components/UI.jsx";
import Intro from "./screens/Intro.jsx";
import ClubProfile from "./screens/ClubProfile.jsx";
import Observations from "./screens/Observations.jsx";
import Protocols from "./screens/Protocols.jsx";
import Moments from "./screens/Moments.jsx";
import System from "./screens/System.jsx";

const STEPS = ["Context", "Observations", "Protocols", "Moments", "Brief"];

const INITIAL_CONFIG = {
  clubName: "",
  team: null,
  contexts: [],
  observations: [],
  timings: [],
  scope: null,
  obsNotes: "",
  currentUse: [],
  protocolNotes: "",
  validator: null,
  constraints: [],
  moments: [],
};

export default function App() {
  const [step, setStep] = useState(0);
  const [config, setConfig] = useState(INITIAL_CONFIG);
  const [generating, setGenerating] = useState(false);

  // Accepts an object patch or a function (prevConfig) => patch, so rapid
  // successive interactions never work from stale state.
  const update = (patch) =>
    setConfig((c) => ({ ...c, ...(typeof patch === "function" ? patch(c) : patch) }));
  const next = () => setStep((s) => Math.min(s + 1, 5));
  const back = () => setStep((s) => Math.max(s - 1, 0));
  const restart = () => {
    setConfig(INITIAL_CONFIG);
    setStep(0);
  };

  // Final step → cinematic compile → Confidential Performance Brief reveal
  const generateSystem = () => {
    setGenerating(true);
    setTimeout(() => {
      setStep(5);
      setGenerating(false);
    }, 2400);
  };

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, [step]);

  const canContinue =
    step === 1
      ? config.clubName.trim() && config.team && config.contexts.length > 0
      : step === 2
        ? config.observations.length > 0 && config.timings.length > 0 && config.scope
        : step === 3
          ? config.validator && (config.currentUse.length > 0 || config.protocolNotes.trim())
          : step === 4
            ? config.moments.length > 0
            : true;

  const screens = [
    <Intro key="intro" next={next} />,
    <ClubProfile key="profile" config={config} update={update} />,
    <Observations key="observations" config={config} update={update} />,
    <Protocols key="protocols" config={config} update={update} />,
    <Moments key="moments" config={config} update={update} />,
    <System key="brief" config={config} restart={restart} />,
  ];

  return (
    <div className="relative min-h-screen">
      <Backdrop />

      {/* Header */}
      <header className="relative z-20 mx-auto flex max-w-6xl items-center justify-between px-6 pb-2 pt-6 md:pt-8">
        <button onClick={restart} className="flex items-center gap-2.5">
          <DreamfruitMark size={30} />
          <span className="font-display text-[15px] tracking-[0.14em] text-white">DREAMFRUIT</span>
          <span className="hidden text-[9px] font-semibold uppercase tracking-[0.3em] text-white/35 sm:inline">
            Performance Matrix™
          </span>
        </button>

        {step > 0 && (
          <nav className="flex items-center gap-2 md:gap-4">
            {STEPS.map((label, i) => {
              const idx = i + 1;
              const active = step === idx;
              const done = step > idx;
              return (
                <div key={label} className="flex items-center gap-2">
                  <span
                    className="h-1.5 w-1.5 rounded-full transition-all duration-500"
                    style={{
                      background: active ? "#e02875" : done ? "rgba(224,40,117,0.5)" : "rgba(255,255,255,0.15)",
                      boxShadow: active ? "0 0 12px #e02875" : "none",
                    }}
                  />
                  <span
                    className={`hidden text-[10px] font-semibold uppercase tracking-[0.2em] transition-colors md:inline ${
                      active ? "text-white" : "text-white/30"
                    }`}
                  >
                    {label}
                  </span>
                </div>
              );
            })}
          </nav>
        )}
      </header>

      {/* Screen */}
      <main className={`relative z-10 mx-auto max-w-6xl px-6 pt-8 md:pt-12 ${step > 0 && step < 5 ? "pb-40" : "pb-20"}`}>
        <AnimatePresence mode="wait">
          <motion.div key={step} variants={screenVariants} initial="hidden" animate="show" exit="exit">
            {screens[step]}
          </motion.div>
        </AnimatePresence>
      </main>

      {/* Wizard nav */}
      <AnimatePresence>
        {step > 0 && step < 5 && (
          <motion.footer
            initial={{ y: 90, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: 90, opacity: 0 }}
            transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
            className="fixed inset-x-0 bottom-0 z-30 pb-5 pt-10"
            style={{ background: "linear-gradient(180deg, transparent, rgba(5,6,10,0.92) 45%)" }}
          >
            <div className="mx-auto flex max-w-6xl items-center justify-between px-6">
              <motion.button
                whileHover={{ x: -3 }}
                onClick={back}
                className="text-[12px] font-semibold uppercase tracking-[0.22em] text-white/45 transition-colors hover:text-white"
              >
                ← Back
              </motion.button>

              <div className="hidden text-[10px] uppercase tracking-[0.26em] text-white/25 md:block">
                Step {step} of {STEPS.length}
              </div>

              <motion.button
                whileHover={canContinue ? { scale: 1.04 } : {}}
                whileTap={canContinue ? { scale: 0.96 } : {}}
                onClick={() => canContinue && (step === 4 ? generateSystem() : next())}
                disabled={!canContinue}
                className={`rounded-full px-8 py-3.5 text-[12px] font-semibold uppercase tracking-[0.22em] text-white transition-opacity ${
                  canContinue ? "" : "cursor-not-allowed opacity-25"
                }`}
                style={{
                  background: "linear-gradient(120deg, #e02875, #ff4f9a)",
                  boxShadow: canContinue ? "0 0 34px rgba(224,40,117,0.35)" : "none",
                }}
              >
                {step === 4 ? "Generate Performance Brief" : "Continue"} →
              </motion.button>
            </div>
          </motion.footer>
        )}
      </AnimatePresence>

      {/* System compile overlay */}
      <AnimatePresence>
        {generating && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0, transition: { duration: 0.6 } }}
            className="fixed inset-0 z-50 flex flex-col items-center justify-center"
            style={{ background: "rgba(3,4,8,0.96)", backdropFilter: "blur(20px)" }}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
              className="flex items-center gap-3"
            >
              <DreamfruitMark size={38} />
              <span className="font-display text-[20px] tracking-[0.18em] text-white">DREAMFRUIT</span>
            </motion.div>
            <motion.div
              animate={{ opacity: [0.3, 1, 0.3] }}
              transition={{ duration: 1.6, repeat: Infinity }}
              className="mt-3 text-[10px] font-semibold uppercase tracking-[0.32em] text-white/40"
            >
              Compiling your performance brief
            </motion.div>
            <div className="mt-8 h-[3px] w-64 overflow-hidden rounded-full bg-white/8">
              <motion.div
                className="h-full rounded-full"
                style={{ background: "linear-gradient(90deg, #e02875, #ff4f9a, #c8e63d)" }}
                initial={{ width: "0%" }}
                animate={{ width: "100%" }}
                transition={{ duration: 2.1, ease: [0.3, 0.6, 0.4, 1] }}
              />
            </div>
            <motion.div
              className="mt-6 flex flex-col items-center gap-1.5 text-[10px] uppercase tracking-[0.24em] text-white/25"
            >
              {["Observation patterns", "Current protocols", "Architectural directions"].map((t, i) => (
                <motion.span
                  key={t}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: [0, 1, 0.35] }}
                  transition={{ delay: 0.3 + i * 0.6, duration: 0.9 }}
                >
                  ✓ {t}
                </motion.span>
              ))}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
