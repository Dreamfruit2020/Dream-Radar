/**
 * Dream OS — data layer.
 * Everything the configurator renders is driven from here, so future
 * integrations (athlete data, wearables, bloodwork, AI recommendations,
 * manufacturing) can replace these static structures with live services.
 */

export const TEAMS = [
  { id: "mens", label: "Men's First Team", sub: "Senior squad", players: 26 },
  { id: "womens", label: "Women's First Team", sub: "Senior squad", players: 24 },
  { id: "academy", label: "Academy", sub: "Development group", players: 40 },
  { id: "individual", label: "Individual Athlete", sub: "Single protocol", players: 1 },
];

export const OBJECTIVES = [
  { id: "readiness", icon: "🏟", label: "Improve Matchday Readiness", desc: "Peak state when it counts" },
  { id: "hydration", icon: "💧", label: "Improve Hydration", desc: "Fluid and electrolyte precision" },
  { id: "recovery", icon: "🌙", label: "Improve Recovery", desc: "Adapt faster between sessions" },
  { id: "cognition", icon: "🧠", label: "Support Focus & Reaction Speed", desc: "Sharper decisions, later into games" },
  { id: "availability", icon: "🛡", label: "Improve Player Availability", desc: "Fewer missed days, more selection" },
  { id: "female", icon: "🌸", label: "Support Female Athlete Physiology", desc: "Cycle-aware performance support" },
  { id: "travel", icon: "✈", label: "Support Travel Resilience", desc: "Away days without the drop-off" },
];

/** Season context — the conditions the squad actually faces (Step 1). */
export const CONTEXTS = [
  { id: "matchday", icon: "🏟", label: "Matchday" },
  { id: "training", icon: "🏃", label: "Training Day" },
  { id: "recoveryday", icon: "🌱", label: "Recovery Day" },
  { id: "travel", icon: "✈", label: "Travel Period" },
  { id: "heat", icon: "🌡", label: "Heat / Humidity" },
  { id: "congestion", icon: "📅", label: "Fixture Congestion" },
];

export const MOMENTS = [
  { id: "morning", time: "06:30", icon: "☀️", label: "Morning", tag: "Activate", desc: "Wake the system. Prime for the day.", color: "#ffb648", perWeek: 7 },
  { id: "pre", time: "09:45", icon: "⚡", label: "Pre-Training", tag: "Prepare", desc: "Blood flow and focus before the session.", color: "#e02875", perWeek: 5 },
  { id: "training", time: "11:00", icon: "🔥", label: "Training", tag: "Charge", desc: "Hydrate and sustain output.", color: "#c8e63d", perWeek: 5 },
  { id: "post", time: "13:30", icon: "🌱", label: "Post-Training", tag: "Recover", desc: "Refuel inside the adaptation window.", color: "#6ee7a0", perWeek: 5 },
  { id: "evening", time: "21:30", icon: "🌙", label: "Evening", tag: "Restore", desc: "Downshift. Support deep sleep.", color: "#8b5cf6", perWeek: 7 },
  { id: "matchday", time: "MD", icon: "🏟", label: "Matchday", tag: "Perform", desc: "The highest-output ninety minutes.", color: "#ffd166", perWeek: 1 },
];

export const PILLARS = [
  {
    id: "activate",
    name: "ACTIVATE",
    purpose: "Prepare body + mind",
    benefits: ["Blood flow", "Energy metabolism", "Cognitive readiness"],
    bases: ["Dragonfruit", "Beetroot", "Citrus"],
    color: "#e02875",
    color2: "#ff4f9a",
  },
  {
    id: "charge",
    name: "CHARGE",
    purpose: "Hydrate + sustain output",
    benefits: ["Electrolyte balance", "Muscle function", "Training intensity"],
    bases: ["Coconut", "Tropical fruit matrix"],
    color: "#c8e63d",
    color2: "#4cc9f0",
  },
  {
    id: "restore",
    name: "RESTORE",
    purpose: "Recover. Adapt. Repeat.",
    benefits: ["Recovery", "Sleep support", "Inflammation balance"],
    bases: ["Cherry", "Pineapple", "Dark berries"],
    color: "#8b5cf6",
    color2: "#d05cf6",
  },
];

/* ── Observation-led intake (BA guidance, v3) ──────────────────────
   The club describes what it observes; Dreamfruit reveals the pattern.
   The club never diagnoses or configures. */

export const OBSERVATIONS = [
  { id: "late-energy", icon: "📉", label: "Late-Game Energy Drop-Off", desc: "Output falls away in the final third of matches", families: ["activate", "charge"] },
  { id: "slow-recovery", icon: "🔄", label: "Slow Recovery Between Fixtures", desc: "Players not fresh for the next session", families: ["restore"] },
  { id: "cramping", icon: "⚡", label: "Cramping / Heavy Sweat Loss", desc: "Especially in heat or long sessions", families: ["charge"] },
  { id: "soft-tissue", icon: "🩹", label: "Soft-Tissue Issue Clusters", desc: "Recurring muscular problems across the squad", families: ["restore", "charge"] },
  { id: "focus-fade", icon: "🧠", label: "Focus Fading Under Fatigue", desc: "Decision quality drops late in games", families: ["activate"] },
  { id: "travel-dips", icon: "✈", label: "Travel-Week Performance Dips", desc: "Away trips cost more than they should", families: ["restore", "activate"] },
  { id: "illness", icon: "🤒", label: "Illness Disrupting Availability", desc: "Bugs moving through the squad", families: ["restore"] },
  { id: "inconsistent-readiness", icon: "🎯", label: "Inconsistent Matchday Readiness", desc: "Same squad, very different starts", families: ["activate"] },
];

export const TIMINGS = [
  { id: "second-half", label: "Second Half" },
  { id: "day-after", label: "Day After Matches" },
  { id: "congested", label: "Congested Weeks" },
  { id: "away", label: "Away Trips" },
  { id: "heat", label: "Hot Conditions" },
  { id: "preseason", label: "Pre-Season" },
  { id: "all-season", label: "Across The Season" },
];

export const SCOPES = [
  { id: "squad", label: "Whole Squad" },
  { id: "positions", label: "Certain Positions" },
  { id: "individuals", label: "Specific Players" },
  { id: "varies", label: "It Varies" },
];

export const CURRENT_USE = [
  { id: "electrolytes", label: "Electrolyte Drinks" },
  { id: "caffeine", label: "Caffeine" },
  { id: "protein", label: "Protein / Carbs" },
  { id: "creatine", label: "Creatine" },
  { id: "gels", label: "Gels / Bars" },
  { id: "vitamins", label: "Vitamins / Omega-3" },
  { id: "club-products", label: "Club-Specific Products" },
  { id: "adhoc", label: "None / Ad-Hoc" },
];

export const VALIDATORS = [
  { id: "nutritionist", label: "Club Nutritionist" },
  { id: "medical", label: "Medical Staff" },
  { id: "external", label: "External Consultant" },
  { id: "none", label: "No Dedicated Validator" },
];

export const CONSTRAINTS = [
  { id: "allergies", label: "Allergies / Intolerances" },
  { id: "vegan", label: "Vegan / Vegetarian Options" },
  { id: "halal", label: "Halal / Kosher Requirements" },
  { id: "digestive", label: "Digestive Sensitivity" },
  { id: "antidoping", label: "Anti-Doping Certification Required" },
  { id: "academy-ages", label: "Academy Age Groups" },
];

/** Families indicated by the observations — revealed by Dreamfruit, never chosen by the club. */
export function indicatedFamilies(config) {
  const counts = { activate: 0, charge: 0, restore: 0 };
  config.observations.forEach((id) => {
    const obs = OBSERVATIONS.find((o) => o.id === id);
    if (obs) obs.families.forEach((f) => (counts[f] += 1));
  });
  return counts;
}

/**
 * Performance needs — the front-end decision layer (per BA guidance).
 * Clubs select needs, not ingredients: bioactive selection, preparation
 * technology and formulation logic sit behind the platform and are
 * developed with the Biological Architect.
 */
export const NEED_GROUPS = [
  {
    id: "performance",
    label: "Performance",
    color: "#e02875",
    items: [
      { id: "matchday-activation", name: "Matchday Activation", desc: "Peak readiness for competition" },
      { id: "oxygen-efficiency", name: "Oxygen Efficiency", desc: "Aerobic output · blood flow" },
      { id: "repeat-sprint", name: "Repeat Sprint Capacity", desc: "Recover between high-intensity efforts" },
      { id: "explosive-power", name: "Explosive Power", desc: "Speed and strength expression" },
      { id: "energy-stability", name: "Second-Half Energy Stability", desc: "No late-game drop-off" },
    ],
  },
  {
    id: "hydration",
    label: "Hydration",
    color: "#c8e63d",
    items: [
      { id: "sweat-loss", name: "Sweat-Loss Compensation", desc: "Replace what the session takes" },
      { id: "heat-load", name: "Heat & Humidity Load", desc: "Perform in hostile conditions" },
      { id: "electrolyte-balance", name: "Electrolyte Balance", desc: "Muscle function · cramp defence" },
      { id: "cellular-fluid", name: "Cellular Fluid Balance", desc: "Hydration at the cellular level" },
    ],
  },
  {
    id: "recovery",
    label: "Recovery",
    color: "#8b5cf6",
    items: [
      { id: "muscle-repair", name: "Muscle Repair", desc: "Rebuild after load" },
      { id: "inflammation", name: "Inflammation Balance", desc: "Manage the response, keep the adaptation" },
      { id: "oxidative-load", name: "Oxidative-Load Management", desc: "Antioxidant support in heavy blocks" },
      { id: "night-recovery", name: "Night-Time Recovery", desc: "Sleep quality and overnight repair" },
      { id: "fixture-congestion", name: "Fixture Congestion Support", desc: "Three games in eight days" },
    ],
  },
  {
    id: "cognition",
    label: "Cognition",
    color: "#4cc9f0",
    items: [
      { id: "focus", name: "Focus", desc: "Sustained attention under fatigue" },
      { id: "reaction-speed", name: "Reaction Speed", desc: "First to every second ball" },
      { id: "decision-making", name: "Decision Making", desc: "Clarity in the final third" },
      { id: "mental-fatigue", name: "Mental Fatigue", desc: "Fresh mind in minute ninety" },
      { id: "stress-load", name: "Stress-Load Regulation", desc: "Pressure without the cost" },
    ],
  },
  {
    id: "specialist",
    label: "Specialist",
    color: "#ffd166",
    items: [
      { id: "female-support", name: "Female Athlete Support", desc: "Cycle-aware physiology support" },
      { id: "travel-support", name: "Travel Support", desc: "Jet lag · resilience on the road" },
      { id: "immunity", name: "Immunity / Availability Support", desc: "Protect selection availability" },
      { id: "return-to-play", name: "Return-to-Play Support", desc: "Back sooner, back stronger" },
      { id: "academy", name: "Academy / Development Support", desc: "Age-appropriate development needs" },
    ],
  },
];

/** Priority levels for a selected need. */
export const LEVELS = ["Off", "Support", "Priority", "Critical"];

/** Moment → generated formula mapping for the final matrix. */
export const FORMULA_MAP = {
  morning: { icon: "⚡", name: "Activate AM", desc: "Morning readiness formula", pillar: "activate" },
  pre: { icon: "⚡", name: "Prime Pre", desc: "Pre-session loading formula", pillar: "activate" },
  training: { icon: "🔥", name: "Training Charge", desc: "Daily hydration system", pillar: "charge" },
  post: { icon: "🌱", name: "Rebuild Post", desc: "Adaptation-window formula", pillar: "restore" },
  evening: { icon: "🌙", name: "Restore PM", desc: "Recovery protocol", pillar: "restore" },
  matchday: { icon: "🏟", name: "Matchday Performance", desc: "High output formula", pillar: "charge" },
};

export const PROGRAMME = {
  name: "2 Month Performance Build",
  months: [
    {
      title: "Month 1 · Discover",
      points: ["Player feedback", "Taste profiling", "Usage occasions", "Performance objectives"],
    },
    {
      title: "Month 2 · Optimise",
      points: ["Formula refinement", "Compliance tracking", "Final protocols"],
    },
  ],
};

/** Final "Club Performance System" formula sheet. A formula appears when its
 *  pillar was chosen or one of its moments is in the schedule. */
export const SYSTEM_FORMULAS = [
  {
    id: "activate",
    icon: "⚡",
    name: "ACTIVATE AM™",
    pillar: "activate",
    purpose: "Prepare body + mind for performance",
    usage: "Morning / Pre-Training",
    matrix: ["Dragonfruit", "Beetroot", "Citrus"],
    layers: ["Nitrate Blend", "Citrulline", "Polyphenol Complex"],
    outcomes: ["Blood Flow", "Energy Metabolism", "Cognitive Readiness"],
    moments: ["morning", "pre"],
  },
  {
    id: "charge",
    icon: "🔥",
    name: "CHARGE™",
    pillar: "charge",
    purpose: "Hydrate + maximise training output",
    usage: "Training / Gym / High Sweat Loss",
    matrix: ["Coconut Water", "Tropical Fruit Matrix"],
    layers: ["Sodium", "Potassium", "Magnesium", "Creatine"],
    outcomes: ["Hydration", "Muscle Function", "Sustained Output"],
    moments: ["training", "matchday"],
  },
  {
    id: "restore",
    icon: "🌙",
    name: "RESTORE PM™",
    pillar: "restore",
    purpose: "Recover. Adapt. Repeat.",
    usage: "Post-Training / Evening",
    matrix: ["Cherry", "Pineapple", "Dark Berry Complex"],
    layers: ["Omega-3", "Anthocyanins", "Polyphenols", "Magnesium"],
    outcomes: ["Recovery Support", "Sleep Preparation", "Adaptation"],
    moments: ["post", "evening"],
  },
];

export function relevantFormulas(config) {
  const list = SYSTEM_FORMULAS.filter(
    (f) => config.pillars.includes(f.pillar) || f.moments.some((m) => config.moments.includes(m))
  );
  return list.length ? list : SYSTEM_FORMULAS;
}

/** Weekly protocol rows derived from the selected moments. */
export function buildProtocol(config) {
  const has = (id) => config.moments.includes(id);
  const training = [
    has("morning") && { slot: "Morning", formula: "Activate AM", icon: "☀️" },
    has("pre") && { slot: "Pre-Training", formula: "Activate AM", icon: "⚡" },
    has("training") && { slot: "During Training", formula: "Charge", icon: "🔥" },
    has("post") && { slot: "Post-Training", formula: "Restore PM", icon: "🌱" },
    has("evening") && { slot: "Evening", formula: "Restore PM", icon: "🌙" },
  ].filter(Boolean);
  const matchday = has("matchday")
    ? [
        { slot: "Pre-Match", formula: "Activate Performance", icon: "⚡" },
        { slot: "Post-Match", formula: "Restore Recovery", icon: "🌙" },
      ]
    : [];
  return { training, matchday };
}

/** Simple serving model — replaced later by squad scheduling + AI. */
export function estimateBottlesPerWeek(config) {
  const team = TEAMS.find((t) => t.id === config.team);
  const players = team ? team.players : 26;
  const servings = config.moments.reduce((sum, id) => {
    const m = MOMENTS.find((x) => x.id === id);
    return sum + (m ? m.perWeek : 0);
  }, 0);
  return Math.max(servings * players, players);
}
