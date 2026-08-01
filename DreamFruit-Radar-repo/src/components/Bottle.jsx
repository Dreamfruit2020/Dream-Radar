import { motion } from "framer-motion";

/**
 * DragonAid bottle — modelled on the real Dreamfruit DragonAid product:
 * wide juice bottle, white cap, DREAMFRUIT arc badge, two-tone power arrow,
 * vertical DRAGONAID type, POWER variant word, dragonfruit-spike base row.
 * `layers` = [{ color, intensity (1-3) }] → glowing configurator auras.
 */
export default function Bottle({
  layers = [],
  color = "#e02875",
  color2 = "#ff4f9a",
  variant = "POWER UP",
  className = "",
}) {
  const auras = layers.slice(0, 8);
  const spikes = Array.from({ length: 7 });

  return (
    <svg viewBox="0 0 320 460" className={className} fill="none">
      <defs>
        <linearGradient id="liquid" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color2} stopOpacity="0.98" />
          <stop offset="100%" stopColor={color} stopOpacity="0.96" />
        </linearGradient>
        <linearGradient id="capShade" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="#e8e8e2" />
          <stop offset="50%" stopColor="#ffffff" />
          <stop offset="100%" stopColor="#d9d9d3" />
        </linearGradient>
        <filter id="soft" x="-60%" y="-60%" width="220%" height="220%">
          <feGaussianBlur stdDeviation="14" />
        </filter>
        <clipPath id="bodyClip">
          <path d="M108 142 q0-30 30-30 h44 q30 0 30 30 v240 q0 28-28 28 h-48 q-28 0-28-28 Z" />
        </clipPath>
        <path id="dfBadgeArc" d="M126 172 Q160 160 194 172" fill="none" />
      </defs>

      {/* glow bed */}
      <ellipse cx="160" cy="260" rx="115" ry="150" fill={color} opacity="0.17" filter="url(#soft)" className="pulse-glow" />

      {/* ingredient auras */}
      {auras.map((l, i) => (
        <motion.rect
          key={i}
          initial={{ opacity: 0, scale: 0.86 }}
          animate={{ opacity: 0.16 + Math.min(l.intensity, 3) * 0.1, scale: 1 }}
          transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
          x={98 - i * 11}
          y={102 - i * 11}
          width={124 + i * 22}
          height={318 + i * 22}
          rx={42 + i * 8}
          stroke={l.color}
          strokeWidth="1.6"
          style={{ transformOrigin: "160px 261px" }}
        />
      ))}

      {/* orbit rings */}
      <g className="spin-slow" style={{ transformOrigin: "160px 261px" }}>
        <circle cx="160" cy="261" r="148" stroke="rgba(255,255,255,0.14)" strokeWidth="1" strokeDasharray="2 9" />
      </g>
      <g className="spin-slower" style={{ transformOrigin: "160px 261px" }}>
        <circle cx="160" cy="261" r="170" stroke={color} strokeOpacity="0.3" strokeWidth="1" strokeDasharray="1 14" />
      </g>

      {/* white screw cap with ridges */}
      <rect x="128" y="52" width="64" height="34" rx="6" fill="url(#capShade)" stroke="#c9c9c2" />
      {[0, 1, 2, 3, 4, 5, 6].map((r) => (
        <line key={r} x1={134 + r * 9} y1="56" x2={134 + r * 9} y2="82" stroke="rgba(0,0,0,0.08)" strokeWidth="2" />
      ))}
      {/* neck + shoulder */}
      <path d="M132 86 h56 v14 q0 8 10 12 h-76 q10-4 10-12 Z" fill="rgba(255,255,255,0.08)" stroke="rgba(255,255,255,0.18)" />

      {/* body */}
      <path
        d="M108 142 q0-30 30-30 h44 q30 0 30 30 v240 q0 28-28 28 h-48 q-28 0-28-28 Z"
        fill="rgba(255,255,255,0.03)"
        stroke="rgba(255,255,255,0.22)"
        strokeWidth="1.5"
      />

      <g clipPath="url(#bodyClip)">
        {/* juice fill — full bottle */}
        <motion.rect
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1.2 }}
          x="104"
          y="108"
          width="120"
          height="310"
          fill="url(#liquid)"
        />
        {/* pulp texture + rising bubbles */}
        {[0, 1, 2, 3, 4].map((b) => (
          <motion.circle
            key={b}
            cx={126 + b * 17}
            r={2 + (b % 3)}
            fill="rgba(255,255,255,0.45)"
            initial={{ cy: 400, opacity: 0 }}
            animate={{ cy: 190, opacity: [0, 0.6, 0] }}
            transition={{ duration: 3.4 + b * 0.7, repeat: Infinity, delay: b * 0.9, ease: "easeOut" }}
          />
        ))}
        {/* condensation droplets */}
        {[[118, 200], [212, 240], [116, 300], [208, 330], [124, 370], [204, 180]].map(([cx, cy], i) => (
          <circle key={i} cx={cx} cy={cy} r={1.6 + (i % 2)} fill="rgba(255,255,255,0.35)" />
        ))}

        {/* DREAMFRUIT arc badge */}
        <path
          d="M122 176 Q160 162 198 176 L198 186 Q160 172 122 186 Z"
          fill="#f7f7f2"
          stroke="#2b0d16"
          strokeWidth="1.6"
          strokeLinejoin="round"
        />
        <text fontSize="8" letterSpacing="1.6" fill="#141014" fontWeight="700" fontFamily="inherit">
          <textPath href="#dfBadgeArc" startOffset="50%" textAnchor="middle">
            DREAMFRUIT
          </textPath>
        </text>

        {/* two-tone power arrow */}
        <g opacity="0.95">
          <path
            d="M150 196 L112 252 L138 246 L138 356 L162 356 L162 246 L188 252 Z"
            fill="#c8e63d"
            transform="translate(-6 -4)"
            opacity="0.85"
          />
          <path
            d="M166 200 L128 256 L154 250 L154 360 L178 360 L178 250 L204 256 Z"
            fill={color === "#c8e63d" ? "#e02875" : "#ff2d6f"}
            opacity="0.9"
          />
        </g>

        {/* vertical DRAGONAID type */}
        <text
          transform="rotate(-90 160 272)"
          x="160"
          y="272"
          textAnchor="middle"
          dominantBaseline="middle"
          fontSize="27"
          letterSpacing="1.5"
          fill="#ffffff"
          stroke="rgba(20,16,20,0.35)"
          strokeWidth="0.8"
          fontFamily="'Archivo Black', Inter, sans-serif"
        >
          DRAGONAID
        </text>

        {/* POWER variant */}
        <text
          x="160"
          y="392"
          textAnchor="middle"
          fontSize="15"
          letterSpacing="0.5"
          fill="#ffffff"
          fontFamily="'Archivo Black', Inter, sans-serif"
          transform="skewX(-6)"
        >
          {variant}
        </text>

        {/* dragonfruit spike rows at the base */}
        <g stroke="#2b0d16" strokeWidth="1.4" strokeLinejoin="round">
          {spikes.map((_, i) => (
            <path
              key={`b${i}`}
              d={`M${102 + i * 18} 436 C${102 + i * 18} 420 ${108 + i * 18} 412 ${111 + i * 18} 408 C${114 + i * 18} 412 ${120 + i * 18} 420 ${120 + i * 18} 436 Z`}
              fill={i % 2 ? "#c8e63d" : "#7cc832"}
            />
          ))}
          {spikes.map((_, i) => (
            <path
              key={`f${i}`}
              d={`M${111 + i * 18} 442 C${111 + i * 18} 428 ${117 + i * 18} 420 ${120 + i * 18} 416 C${123 + i * 18} 420 ${129 + i * 18} 428 ${129 + i * 18} 442 Z`}
              fill={i % 2 ? color2 : color}
            />
          ))}
        </g>
      </g>

      {/* glass sheen */}
      <g clipPath="url(#bodyClip)">
        <rect x="118" y="120" width="9" height="290" rx="4.5" fill="rgba(255,255,255,0.28)" />
        <rect x="200" y="130" width="4" height="270" rx="2" fill="rgba(255,255,255,0.14)" />
      </g>
    </svg>
  );
}
