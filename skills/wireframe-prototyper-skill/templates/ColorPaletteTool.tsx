import { useState, useRef, useEffect, useMemo, useCallback } from "react";
import {
  Palette,
  RotateCcw,
  X,
  ChevronDown,
  ChevronUp,
  Undo2,
  Plus,
  Save,
  Copy,
  Check,
  Pipette,
  Download,
  Upload,
  Pencil,
} from "lucide-react";
import {
  useDesignSystem,
  DS_PRESETS,
  DSColorKey,
  DS_TOKEN_KEYS,
  type CustomPreset,
} from "@/contexts/DesignSystemContext";

/* ─── WCAG Contrast Ratio Utilities ─── */
function hexToRgb(hex: string): [number, number, number] {
  const h = hex.replace("#", "");
  return [
    parseInt(h.substring(0, 2), 16),
    parseInt(h.substring(2, 4), 16),
    parseInt(h.substring(4, 6), 16),
  ];
}

function relativeLuminance(r: number, g: number, b: number): number {
  const [rs, gs, bs] = [r / 255, g / 255, b / 255].map(c =>
    c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4)
  );
  return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
}

function contrastRatio(hex1: string, hex2: string): number {
  const [r1, g1, b1] = hexToRgb(hex1);
  const [r2, g2, b2] = hexToRgb(hex2);
  const l1 = relativeLuminance(r1, g1, b1);
  const l2 = relativeLuminance(r2, g2, b2);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

type WCAGLevel = "AAA" | "AA" | "FAIL";

function getWCAGLevel(ratio: number, isLargeText = false): WCAGLevel {
  if (isLargeText) {
    if (ratio >= 4.5) return "AAA";
    if (ratio >= 3) return "AA";
    return "FAIL";
  }
  if (ratio >= 7) return "AAA";
  if (ratio >= 4.5) return "AA";
  return "FAIL";
}

/* ─── Contrast Pair Definitions (M3) ─── */
type ContrastPair = { bg: DSColorKey; fg: DSColorKey; label: string };

const CONTRAST_PAIRS: ContrastPair[] = [
  { bg: "primary", fg: "onPrimary", label: "Primary / On Primary" },
  {
    bg: "primaryContainer",
    fg: "onPrimaryContainer",
    label: "Primary Container / On Primary Container",
  },
  { bg: "secondary", fg: "onSecondary", label: "Secondary / On Secondary" },
  {
    bg: "secondaryContainer",
    fg: "onSecondaryContainer",
    label: "Secondary Container / On Secondary Container",
  },
  { bg: "tertiary", fg: "onTertiary", label: "Tertiary / On Tertiary" },
  {
    bg: "tertiaryContainer",
    fg: "onTertiaryContainer",
    label: "Tertiary Container / On Tertiary Container",
  },
  { bg: "surface", fg: "onSurface", label: "Surface / On Surface" },
  {
    bg: "surfaceVariant",
    fg: "onSurfaceVariant",
    label: "Surface Variant / On Surface Variant",
  },
  {
    bg: "surfaceContainerLowest",
    fg: "onSurface",
    label: "Surface Container Lowest / On Surface",
  },
  {
    bg: "surfaceContainerHighest",
    fg: "onSurface",
    label: "Surface Container Highest / On Surface",
  },
  {
    bg: "inverseSurface",
    fg: "inverseOnSurface",
    label: "Inverse Surface / Inverse On Surface",
  },
  { bg: "success", fg: "onSuccess", label: "Success / On Success" },
  {
    bg: "successContainer",
    fg: "onSuccessContainer",
    label: "Success Container / On Success Container",
  },
  { bg: "error", fg: "onError", label: "Error / On Error" },
  {
    bg: "errorContainer",
    fg: "onErrorContainer",
    label: "Error Container / On Error Container",
  },
];

/* ─── Token Groups (M3 organization — matching screenshot) ─── */
const TOKEN_GROUPS: {
  label: string;
  tokens: { key: DSColorKey; label: string }[];
}[] = [
  {
    label: "Primary",
    tokens: [
      { key: "primary", label: "Primary" },
      { key: "onPrimary", label: "On Primary" },
      { key: "primaryContainer", label: "Primary Container" },
      { key: "onPrimaryContainer", label: "On Primary Container" },
    ],
  },
  {
    label: "Secondary",
    tokens: [
      { key: "secondary", label: "Secondary" },
      { key: "onSecondary", label: "On Secondary" },
      { key: "secondaryContainer", label: "Secondary Container" },
      { key: "onSecondaryContainer", label: "On Secondary Container" },
    ],
  },
  {
    label: "Tertiary",
    tokens: [
      { key: "tertiary", label: "Tertiary" },
      { key: "onTertiary", label: "On Tertiary" },
      { key: "tertiaryContainer", label: "Tertiary Container" },
      { key: "onTertiaryContainer", label: "On Tertiary Container" },
    ],
  },
  {
    label: "Success",
    tokens: [
      { key: "success", label: "Success" },
      { key: "onSuccess", label: "On Success" },
      { key: "successContainer", label: "Success Container" },
      { key: "onSuccessContainer", label: "On Success Container" },
    ],
  },
  {
    label: "Error",
    tokens: [
      { key: "error", label: "Error" },
      { key: "onError", label: "On Error" },
      { key: "errorContainer", label: "Error Container" },
      { key: "onErrorContainer", label: "On Error Container" },
    ],
  },
  {
    label: "Surface",
    tokens: [
      { key: "surface", label: "Surface" },
      { key: "onSurface", label: "On Surface" },
      { key: "surfaceVariant", label: "Surface Variant" },
      { key: "onSurfaceVariant", label: "On Surface Variant" },
    ],
  },
  {
    label: "Surface Containers",
    tokens: [
      { key: "surfaceContainerHighest", label: "Surface Container Highest" },
      { key: "surfaceContainerHigh", label: "Surface Container High" },
      { key: "surfaceContainer", label: "Surface Container" },
      { key: "surfaceContainerLow", label: "Surface Container Low" },
      { key: "surfaceContainerLowest", label: "Surface Container Lowest" },
    ],
  },
  {
    label: "Inverse & Tint",
    tokens: [
      { key: "inverseSurface", label: "Inverse Surface" },
      { key: "inverseOnSurface", label: "Inverse On Surface" },
      { key: "surfaceTint", label: "Surface Tint" },
      { key: "surfaceTintColor", label: "Surface Tint Color" },
    ],
  },
  {
    label: "Outline",
    tokens: [
      { key: "outline", label: "Outline" },
      { key: "outlineVariant", label: "Outline Variant" },
    ],
  },
];

/* ─── Contrast Badge Component ─── */
function ContrastBadge({ ratio, level }: { ratio: number; level: WCAGLevel }) {
  const bgColor =
    level === "AAA" ? "#059669" : level === "AA" ? "#D97706" : "#DC2626";
  const textColor = "#FFFFFF";
  return (
    <span
      className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[9px] font-bold leading-none"
      style={{ background: bgColor, color: textColor }}
      title={`Contrast ratio: ${ratio.toFixed(2)}:1 — WCAG ${level} (normal text)`}
    >
      {ratio.toFixed(1)}:1
      <span className="opacity-80">{level}</span>
    </span>
  );
}

/* ─── Contrast Pair Row ─── */
function ContrastPairRow({
  pair,
  colors,
}: {
  pair: ContrastPair;
  colors: Record<string, string>;
}) {
  const bgHex = colors[pair.bg] || "#FFFFFF";
  const fgHex = colors[pair.fg] || "#000000";
  const ratio = contrastRatio(bgHex, fgHex);
  const level = getWCAGLevel(ratio);

  return (
    <div className="flex items-center gap-2 py-1.5">
      {/* Mini preview */}
      <div
        className="w-8 h-5 rounded flex items-center justify-center text-[8px] font-bold flex-shrink-0 border border-gray-200"
        style={{ background: bgHex, color: fgHex }}
      >
        Aa
      </div>
      {/* Label */}
      <p className="text-[10px] text-gray-600 flex-1 min-w-0 truncate">
        {pair.label}
      </p>
      {/* Badge */}
      <ContrastBadge ratio={ratio} level={level} />
    </div>
  );
}

function ColorSwatch({
  colorKey,
  label,
  activePresetColors,
  failingPairs,
}: {
  colorKey: DSColorKey;
  label: string;
  activePresetColors: Record<string, string>;
  failingPairs?: { label: string; ratio: number }[];
}) {
  const { colors, setColor } = useDesignSystem();
  const value = colors[colorKey];
  const colorInputRef = useRef<HTMLInputElement>(null);
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(value);
  const [pickerOpen, setPickerOpen] = useState(false);
  const [copied, setCopied] = useState(false);

  // The "original" value for this token from the currently selected preset
  const presetValue = activePresetColors[colorKey] || value;
  const isModified = value.toLowerCase() !== presetValue.toLowerCase();

  // Keep draft in sync when value changes externally (e.g. preset switch)
  useEffect(() => {
    if (!editing) setDraft(value);
  }, [value, editing]);

  const commitDraft = () => {
    setEditing(false);
    const hex = draft.startsWith("#") ? draft : `#${draft}`;
    // Validate hex format
    if (/^#[0-9A-Fa-f]{6}$/.test(hex)) {
      setColor(colorKey, hex.toUpperCase());
      setDraft(hex.toUpperCase());
    } else {
      setDraft(value); // revert
    }
  };

  return (
    <div className="flex items-center gap-1.5 py-1">
      <button
        className="w-8 h-8 rounded-md border border-gray-200 flex-shrink-0 cursor-pointer relative overflow-hidden"
        style={{ background: value }}
        onClick={() => {
          if (pickerOpen) {
            setPickerOpen(false);
          } else {
            setPickerOpen(true);
            colorInputRef.current?.click();
          }
        }}
        title={`${label}: ${value}`}
      >
        <input
          ref={colorInputRef}
          type="color"
          value={value}
          onChange={e => setColor(colorKey, e.target.value.toUpperCase())}
          onBlur={() => setPickerOpen(false)}
          className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
        />
      </button>
      <div className="flex-1 min-w-0">
        <p className="text-[11px] font-medium text-gray-700 truncate leading-none">
          {label}
        </p>
        {editing ? (
          <input
            autoFocus
            type="text"
            value={draft}
            onChange={e => setDraft(e.target.value)}
            onBlur={commitDraft}
            onKeyDown={e => {
              if (e.key === "Enter") commitDraft();
              if (e.key === "Escape") {
                setDraft(value);
                setEditing(false);
              }
            }}
            className="text-[10px] font-mono uppercase w-full bg-gray-50 border border-gray-200 rounded px-1 py-0.5 outline-none focus:border-indigo-400 text-gray-700"
            maxLength={7}
          />
        ) : (
          <button
            onClick={() => {
              setDraft(value);
              setEditing(true);
            }}
            className="text-[10px] text-gray-400 font-mono uppercase hover:text-gray-600 hover:bg-gray-100 rounded px-0.5 transition-colors cursor-text leading-none"
          >
            {value}
          </button>
        )}
      </div>
      {/* WCAG warning */}
      {failingPairs && failingPairs.length > 0 && (
        <span
          className="flex-shrink-0"
          title={`WCAG contrast failure: ${failingPairs.map(p => `${p.label} (${p.ratio.toFixed(1)}:1)`).join(", ")}`}
        >
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="#DC2626"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
            <line x1="12" y1="9" x2="12" y2="13" />
            <line x1="12" y1="17" x2="12.01" y2="17" />
          </svg>
        </span>
      )}
      {/* Copy button */}
      <button
        onClick={() => {
          navigator.clipboard.writeText(value);
          setCopied(true);
          setTimeout(() => setCopied(false), 1200);
        }}
        className="p-1 rounded transition-colors flex-shrink-0 text-gray-300 hover:text-gray-600 hover:bg-gray-100 cursor-pointer"
        title="Copy hex value"
      >
        {copied ? (
          <Check size={10} className="text-green-500" />
        ) : (
          <Copy size={10} />
        )}
      </button>
      {/* Reset-to-preset button */}
      <button
        onClick={() => setColor(colorKey, presetValue)}
        className={`p-1 rounded transition-colors flex-shrink-0 ${
          isModified
            ? "text-black hover:text-gray-700 hover:bg-gray-100 cursor-pointer"
            : "text-gray-200 cursor-default"
        }`}
        title={
          isModified
            ? `Reset to preset value (${presetValue})`
            : "Matches preset"
        }
        disabled={!isModified}
      >
        <Undo2 size={12} />
      </button>
    </div>
  );
}

export default function ColorPaletteTool() {
  const [open, setOpen] = useState(false);
  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>(
    {
      Primary: true,
      Secondary: false,
      Tertiary: false,
      Error: false,
      Surface: false,
      "Surface Containers": false,
      "Inverse & Tint": false,
      Outline: false,
      "Contrast Checker": false,
    }
  );
  const {
    colors,
    setColors,
    resetColors,
    customPresets,
    saveCustomPreset,
    updateCustomPreset,
    renameCustomPreset,
    deleteCustomPreset,
    activePresetId,
    setActivePresetId,
  } = useDesignSystem();
  const [showSaveInput, setShowSaveInput] = useState(false);
  const [newPresetName, setNewPresetName] = useState("");
  const [renamingPresetId, setRenamingPresetId] = useState<string | null>(null);
  const [renameValue, setRenameValue] = useState("");
  const [importToastOpacity, setImportToastOpacity] = useState(0);
  const importToastTimers = useRef<ReturnType<typeof setTimeout>[]>([]);
  const panelRef = useRef<HTMLDivElement>(null);

  const showImportToast = () => {
    importToastTimers.current.forEach(clearTimeout);
    importToastTimers.current = [];
    setImportToastOpacity(0);
    // Small delay to ensure opacity:0 is painted before transitioning to 1
    importToastTimers.current.push(
      setTimeout(() => {
        setImportToastOpacity(1);
      }, 50)
    );
    // After 2s, start fade-out
    importToastTimers.current.push(
      setTimeout(() => {
        setImportToastOpacity(0);
      }, 2000)
    );
  };

  // Determine which preset's colours to use for per-token reset (based on explicit selection)
  const activePresetColors = useMemo(() => {
    // Check built-in presets by name
    const builtin = DS_PRESETS.find(p => p.name === activePresetId);
    if (builtin) return builtin.colors as unknown as Record<string, string>;
    // Check custom presets by id
    const custom = customPresets.find(p => p.id === activePresetId);
    if (custom) return custom.colors as unknown as Record<string, string>;
    // Fallback to first built-in
    return DS_PRESETS[0].colors as unknown as Record<string, string>;
  }, [activePresetId, customPresets]);

  // Detect if the active preset is a custom one and has unsaved changes
  const activeCustomPreset = useMemo(() => {
    return customPresets.find(p => p.id === activePresetId) || null;
  }, [customPresets, activePresetId]);

  const hasCustomPresetChanges = useMemo(() => {
    if (!activeCustomPreset) return false;
    return DS_TOKEN_KEYS.some(
      key =>
        colors[key].toLowerCase() !==
        activeCustomPreset.colors[key].toLowerCase()
    );
  }, [activeCustomPreset, colors]);

  // Detect if a built-in preset is selected and has unsaved changes
  const activeBuiltinPreset = useMemo(() => {
    return DS_PRESETS.find(p => p.name === activePresetId) || null;
  }, [activePresetId]);

  const hasBuiltinPresetChanges = useMemo(() => {
    if (!activeBuiltinPreset) return false;
    const presetColors = activeBuiltinPreset.colors as unknown as Record<
      string,
      string
    >;
    return DS_TOKEN_KEYS.some(
      key => colors[key].toLowerCase() !== presetColors[key].toLowerCase()
    );
  }, [activeBuiltinPreset, colors]);

  // Compute contrast summary
  const contrastSummary = useMemo(() => {
    let pass = 0;
    let fail = 0;
    for (const pair of CONTRAST_PAIRS) {
      const bgHex = colors[pair.bg] || "#FFFFFF";
      const fgHex = colors[pair.fg] || "#000000";
      const ratio = contrastRatio(bgHex, fgHex);
      const level = getWCAGLevel(ratio);
      if (level === "FAIL") fail++;
      else pass++;
    }
    return { pass, fail, total: CONTRAST_PAIRS.length };
  }, [colors]);

  /* Close on outside click */
  useEffect(() => {
    if (!open) return;
    const handler = (e: MouseEvent) => {
      if (panelRef.current && !panelRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [open]);

  const toggleGroup = (label: string) => {
    setExpandedGroups(prev => ({ ...prev, [label]: !prev[label] }));
  };

  /* ─── Eyedropper Tool ─── */
  const [eyedropperActive, setEyedropperActive] = useState(false);
  const [eyedropperColor, setEyedropperColor] = useState<string | null>(null);
  const [eyedropperTokens, setEyedropperTokens] = useState<string[]>([]);
  const [eyedropperPos, setEyedropperPos] = useState<{ x: number; y: number }>({
    x: 0,
    y: 0,
  });
  const [eyedropperProp, setEyedropperProp] = useState<string>("background");

  // Canvas-based color conversion that handles ALL CSS color formats (rgb, oklch, lab, etc.)
  const rgbToHex = useMemo(() => {
    const canvas = document.createElement("canvas");
    canvas.width = 1;
    canvas.height = 1;
    const ctx = canvas.getContext("2d", { willReadFrequently: true })!;
    return (color: string): string | null => {
      if (!color || color === "transparent" || color === "rgba(0, 0, 0, 0)")
        return null;
      // Skip CSS keywords that aren't valid canvas colors
      if (/^(none|currentColor|inherit|initial|unset|revert)$/i.test(color))
        return null;
      // Check for zero-alpha colors in any format
      if (/\/\s*0\s*\)$/.test(color)) return null;
      // Use a sentinel color to detect invalid color strings.
      // If the color is invalid, fillStyle won't change from the sentinel.
      ctx.clearRect(0, 0, 1, 1);
      ctx.fillStyle = "#010203"; // sentinel (unlikely to be a real color)
      ctx.fillStyle = color;
      // If fillStyle didn't change, the color was invalid
      if (ctx.fillStyle === "#010203") return null;
      ctx.fillRect(0, 0, 1, 1);
      const imgData = ctx.getImageData(0, 0, 1, 1).data;
      const r = imgData[0],
        g = imgData[1],
        b = imgData[2],
        a = imgData[3];
      if (a === 0) return null;
      return (
        "#" +
        [r, g, b]
          .map(c => c.toString(16).padStart(2, "0"))
          .join("")
          .toUpperCase()
      );
    };
  }, []);

  // Find all matching DS tokens for a hex color
  const findMatchingTokens = useCallback(
    (hex: string): string[] => {
      if (!hex) return [];
      const normalizedHex = hex.toUpperCase();
      const matches: string[] = [];
      for (const key of DS_TOKEN_KEYS) {
        if (colors[key].toUpperCase() === normalizedHex) {
          matches.push(key);
        }
      }
      return matches;
    },
    [colors]
  );

  useEffect(() => {
    if (!eyedropperActive) return;

    const handleMouseMove = (e: MouseEvent) => {
      setEyedropperPos({ x: e.clientX, y: e.clientY });

      // Temporarily hide our tooltip to get the real element underneath
      const tooltip = document.getElementById("eyedropper-tooltip");
      if (tooltip) tooltip.style.pointerEvents = "none";

      const el = document.elementFromPoint(
        e.clientX,
        e.clientY
      ) as HTMLElement | null;
      if (!el) {
        setEyedropperColor(null);
        setEyedropperTokens([]);
        return;
      }
      // Skip the eyedropper overlay and panel elements
      const overlay = document.getElementById("eyedropper-overlay");
      if (overlay && overlay.contains(el)) {
        setEyedropperColor(null);
        setEyedropperTokens([]);
        return;
      }

      let colorValue: string | null = null;
      let propName = "background";

      // 1. Check SVG fill/stroke for SVG elements (path, circle, rect, line, polyline, polygon, svg, use)
      const svgTags = new Set([
        "path",
        "circle",
        "rect",
        "line",
        "polyline",
        "polygon",
        "svg",
        "use",
        "ellipse",
      ]);
      if (svgTags.has(el.tagName.toLowerCase())) {
        const svgComputed = window.getComputedStyle(el);
        // Try stroke first (more visually relevant for icon outlines)
        const stroke = svgComputed.stroke;
        if (stroke && stroke !== "none" && stroke !== "transparent") {
          const hex = rgbToHex(stroke);
          if (hex) {
            colorValue = hex;
            propName = "stroke";
          }
        }
        // Try fill if no stroke color found
        if (!colorValue) {
          const fill = svgComputed.fill;
          if (fill && fill !== "none" && fill !== "transparent") {
            const hex = rgbToHex(fill);
            if (hex) {
              colorValue = hex;
              propName = "fill";
            }
          }
        }
      }

      const computed = window.getComputedStyle(el);
      const hasDirectText = Array.from(el.childNodes).some(
        n => n.nodeType === Node.TEXT_NODE && n.textContent?.trim()
      );

      // 2. For text elements, prefer text color first (avoids semi-transparent overlays showing as black)
      if (!colorValue && hasDirectText) {
        const textColor = computed.color;
        if (textColor) {
          const hex = rgbToHex(textColor);
          if (hex) {
            colorValue = hex;
            propName = "color";
          }
        }
      }

      // 3. Try background-color on the element itself
      if (!colorValue) {
        const bgColor = computed.backgroundColor;
        if (bgColor) {
          const hex = rgbToHex(bgColor);
          if (hex) {
            colorValue = hex;
            propName = "background";
          }
        }
      }

      // 4. Try border color (only if border is actually visible)
      if (!colorValue) {
        const borderWidth = computed.borderWidth;
        const borderStyle = computed.borderStyle;
        const hasVisibleBorder =
          borderWidth &&
          borderWidth !== "0px" &&
          borderStyle &&
          borderStyle !== "none";
        if (hasVisibleBorder) {
          const borderColor = computed.borderColor;
          if (borderColor) {
            const hex = rgbToHex(borderColor);
            if (hex) {
              colorValue = hex;
              propName = "border";
            }
          }
        }
      }

      // 5. Walk up ancestors to find a visible background color
      if (!colorValue) {
        let ancestor = el.parentElement;
        let depth = 0;
        while (ancestor && depth < 10) {
          const ancestorComputed = window.getComputedStyle(ancestor);
          const ancestorBg = ancestorComputed.backgroundColor;
          if (ancestorBg) {
            const hex = rgbToHex(ancestorBg);
            if (hex) {
              colorValue = hex;
              propName = "background";
              break;
            }
          }
          ancestor = ancestor.parentElement;
          depth++;
        }
      }

      // 6. Try pseudo-element colors (::before, ::after)
      if (!colorValue) {
        for (const pseudo of ["::before", "::after"] as const) {
          const pseudoComputed = window.getComputedStyle(el, pseudo);
          const pseudoBg = pseudoComputed.backgroundColor;
          if (pseudoBg) {
            const hex = rgbToHex(pseudoBg);
            if (hex) {
              colorValue = hex;
              propName = `${pseudo} background`;
              break;
            }
          }
          const pseudoColor = pseudoComputed.color;
          if (pseudoColor) {
            const hex = rgbToHex(pseudoColor);
            if (hex) {
              colorValue = hex;
              propName = `${pseudo} color`;
              break;
            }
          }
        }
      }

      setEyedropperColor(colorValue);
      setEyedropperProp(propName);
      setEyedropperTokens(colorValue ? findMatchingTokens(colorValue) : []);
    };

    const handleClick = (e: MouseEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setEyedropperActive(false);
    };

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setEyedropperActive(false);
      }
    };

    // Inject a global style to force crosshair cursor on ALL elements
    const styleEl = document.createElement("style");
    styleEl.id = "eyedropper-cursor-style";
    styleEl.textContent = "* { cursor: crosshair !important; }";
    document.head.appendChild(styleEl);

    document.addEventListener("mousemove", handleMouseMove);
    document.addEventListener("click", handleClick, true);
    document.addEventListener("keydown", handleKeyDown);

    return () => {
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("click", handleClick, true);
      document.removeEventListener("keydown", handleKeyDown);
      const existingStyle = document.getElementById("eyedropper-cursor-style");
      if (existingStyle) existingStyle.remove();
    };
  }, [eyedropperActive, rgbToHex, findMatchingTokens]);

  return (
    <>
      {/* Import success toast */}
      <div className="fixed top-6 left-0 right-0 z-[9998] flex justify-center pointer-events-none">
        <div
          className="transition-all duration-500 ease-in-out"
          style={{
            opacity: importToastOpacity,
            transform: `translateY(${importToastOpacity ? "0" : "-12px"})`,
          }}
        >
          <div className="bg-gray-900/90 text-white text-sm px-5 py-3 rounded-lg shadow-lg flex items-center gap-2">
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.5"
              className="text-green-400"
            >
              <path d="M20 6L9 17l-5-5" />
            </svg>
            Color palette imported successfully
          </div>
        </div>
      </div>

      {/* Eyedropper overlay tooltip */}
      {eyedropperActive && (
        <div
          id="eyedropper-overlay"
          className="fixed inset-0 z-[99999]"
          style={{ cursor: "crosshair", pointerEvents: "none" }}
        >
          {eyedropperColor && (
            <div
              id="eyedropper-tooltip"
              className="fixed z-[99999] flex items-center gap-2 px-2.5 py-1.5 rounded-lg shadow-lg border border-gray-200 bg-white text-[11px] font-mono"
              style={{
                left: eyedropperPos.x + 16,
                top: eyedropperPos.y + 16,
                pointerEvents: "none",
              }}
            >
              <div
                className="w-5 h-5 rounded border border-gray-300 flex-shrink-0"
                style={{ backgroundColor: eyedropperColor }}
              />
              <div className="flex flex-col">
                <span className="text-gray-900 font-semibold">
                  {eyedropperColor}
                </span>
                <span className="text-[9px] text-gray-500">
                  {eyedropperTokens.length > 0 ? (
                    <span className="text-indigo-600 font-medium">
                      {eyedropperTokens.join(", ")}
                    </span>
                  ) : (
                    eyedropperProp
                  )}
                </span>
              </div>
            </div>
          )}
        </div>
      )}
      <div className="relative" ref={panelRef}>
        {/* Trigger button */}
        <button
          onClick={() => setOpen(!open)}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-colors duration-150"
          style={{
            color: open ? "#6366f1" : "#666",
            background: open ? "#f0f0ff" : "#f5f5f5",
          }}
          onMouseEnter={e => {
            if (!open) e.currentTarget.style.background = "#eee";
          }}
          onMouseLeave={e => {
            if (!open) e.currentTarget.style.background = "#f5f5f5";
          }}
          title="Design System Colors"
        >
          <Palette size={13} />
          Colors
        </button>

        {/* Dropdown panel */}
        {open && (
          <div
            className="absolute top-full right-0 mt-2 w-[320px] bg-white rounded-xl shadow-2xl border border-gray-200 z-[9999] flex flex-col"
            style={{ maxHeight: "85vh" }}
          >
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100 flex-shrink-0">
              <h3 className="text-sm font-semibold text-gray-900">
                Design System Colors
              </h3>
              <div className="flex items-center gap-1">
                <button
                  onClick={() => {
                    setEyedropperActive(true);
                    setOpen(false);
                  }}
                  className={`p-1.5 rounded-md transition-colors ${
                    eyedropperActive
                      ? "text-indigo-600 bg-indigo-50"
                      : "text-gray-400 hover:text-gray-600 hover:bg-gray-100"
                  }`}
                  title="Eyedropper — pick color from page"
                >
                  <Pipette size={14} />
                </button>
                <button
                  onClick={() => setOpen(false)}
                  className="p-1.5 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
                >
                  <X size={14} />
                </button>
              </div>
            </div>

            {/* Presets */}
            <div
              className="px-4 py-3 border-b border-gray-100 flex-shrink-0 overflow-y-auto"
              style={{ maxHeight: "40vh" }}
            >
              <p className="text-[10px] font-semibold uppercase tracking-wider text-gray-400 mb-2">
                Built-in Presets
              </p>
              <div className="flex flex-wrap gap-1.5">
                {DS_PRESETS.map(preset => {
                  const isActive = activePresetId === preset.name;
                  return (
                    <button
                      key={preset.name}
                      onClick={() => {
                        setColors(preset.colors);
                        setActivePresetId(preset.name);
                      }}
                      className={`flex items-center gap-1.5 px-2 py-1 rounded-md text-[11px] font-medium border transition-colors ${
                        isActive
                          ? "border-indigo-400 bg-indigo-50 text-indigo-700"
                          : "border-gray-200 hover:border-gray-400 hover:bg-gray-50 text-gray-600"
                      }`}
                      title={preset.name}
                    >
                      {/* Mini color preview dots */}
                      <div className="flex -space-x-0.5">
                        <span
                          className="w-3 h-3 rounded-full border border-white"
                          style={{ background: preset.colors.primary }}
                        />
                        <span
                          className="w-3 h-3 rounded-full border border-white"
                          style={{ background: preset.colors.secondary }}
                        />
                        <span
                          className="w-3 h-3 rounded-full border border-white"
                          style={{ background: preset.colors.tertiary }}
                        />
                      </div>
                      <span>{preset.name}</span>
                    </button>
                  );
                })}
              </div>

              {/* Custom Presets */}
              {customPresets.length > 0 && (
                <>
                  <p className="text-[10px] font-semibold uppercase tracking-wider text-gray-400 mt-3 mb-2">
                    Custom Presets
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {customPresets.map((preset: CustomPreset) => {
                      const isActive = activePresetId === preset.id;
                      const isRenaming = renamingPresetId === preset.id;
                      return (
                        <div key={preset.id} className="relative">
                          {isRenaming ? (
                            <div className="flex items-center gap-1 px-2 py-1 rounded-md text-[11px] font-medium border border-indigo-400 bg-indigo-50">
                              <input
                                type="text"
                                value={renameValue}
                                onChange={e => setRenameValue(e.target.value)}
                                onKeyDown={e => {
                                  if (e.key === "Enter" && renameValue.trim()) {
                                    renameCustomPreset(
                                      preset.id,
                                      renameValue.trim()
                                    );
                                    setRenamingPresetId(null);
                                  }
                                  if (e.key === "Escape")
                                    setRenamingPresetId(null);
                                }}
                                onBlur={() => {
                                  if (renameValue.trim())
                                    renameCustomPreset(
                                      preset.id,
                                      renameValue.trim()
                                    );
                                  setRenamingPresetId(null);
                                }}
                                autoFocus
                                className="w-16 bg-transparent outline-none text-[11px] text-indigo-700"
                              />
                              <span
                                onMouseDown={e => {
                                  e.stopPropagation();
                                  e.preventDefault();
                                  if (renameValue.trim()) {
                                    renameCustomPreset(
                                      preset.id,
                                      renameValue.trim()
                                    );
                                  }
                                  setRenamingPresetId(null);
                                }}
                                className="text-indigo-500 hover:text-indigo-700 cursor-pointer"
                              >
                                <Check size={10} />
                              </span>
                            </div>
                          ) : (
                            <button
                              onClick={() => {
                                setColors(preset.colors);
                                setActivePresetId(preset.id);
                              }}
                              className={`group relative flex items-center gap-1.5 px-2 py-1 rounded-md text-[11px] font-medium border transition-colors ${
                                isActive
                                  ? "border-indigo-400 bg-indigo-50 text-indigo-700"
                                  : "border-gray-200 hover:border-gray-400 hover:bg-gray-50 text-gray-600"
                              }`}
                              title={preset.name}
                            >
                              <div className="flex -space-x-0.5">
                                <span
                                  className="w-3 h-3 rounded-full border border-white"
                                  style={{ background: preset.colors.primary }}
                                />
                                <span
                                  className="w-3 h-3 rounded-full border border-white"
                                  style={{
                                    background: preset.colors.secondary,
                                  }}
                                />
                                <span
                                  className="w-3 h-3 rounded-full border border-white"
                                  style={{ background: preset.colors.tertiary }}
                                />
                              </div>
                              <span
                                onDoubleClick={e => {
                                  e.stopPropagation();
                                  setRenamingPresetId(preset.id);
                                  setRenameValue(preset.name);
                                }}
                              >
                                {preset.name}
                              </span>
                              {/* Rename icon */}
                              <span
                                onClick={e => {
                                  e.stopPropagation();
                                  setRenamingPresetId(preset.id);
                                  setRenameValue(preset.name);
                                }}
                                className="ml-0.5 text-gray-400 hover:text-indigo-500 cursor-pointer"
                                title={`Rename "${preset.name}"`}
                              >
                                <Pencil size={10} />
                              </span>
                              {/* Delete icon */}
                              <span
                                onClick={e => {
                                  e.stopPropagation();
                                  deleteCustomPreset(preset.id);
                                }}
                                className="ml-0.5 text-gray-400 hover:text-red-500 cursor-pointer"
                                title={`Delete "${preset.name}"`}
                              >
                                <X size={10} />
                              </span>
                            </button>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </>
              )}

              {/* Update / Reset Custom Preset — only shown when a custom preset is selected and has changes */}
              {activeCustomPreset && hasCustomPresetChanges && (
                <div className="mt-3 flex items-center gap-2">
                  <button
                    onClick={() => updateCustomPreset(activeCustomPreset.id)}
                    className="flex items-center gap-1.5 px-2 py-1.5 rounded-md text-[11px] font-medium bg-indigo-500 text-white hover:bg-indigo-600 transition-colors flex-1 justify-center"
                  >
                    <Save size={11} />
                    Update Preset
                  </button>
                  <button
                    onClick={() => setColors(activeCustomPreset.colors)}
                    className="flex items-center gap-1.5 px-2 py-1.5 rounded-md text-[11px] font-medium border border-gray-300 text-gray-600 hover:bg-gray-100 transition-colors flex-1 justify-center"
                  >
                    <RotateCcw size={11} />
                    Reset Changes
                  </button>
                </div>
              )}

              {/* Reset for built-in preset — only shown when a built-in preset is selected and has changes */}
              {activeBuiltinPreset && hasBuiltinPresetChanges && (
                <div className="mt-3">
                  <button
                    onClick={() =>
                      setColors(
                        activeBuiltinPreset.colors as unknown as Record<
                          string,
                          string
                        >
                      )
                    }
                    className="flex items-center gap-1.5 px-2 py-1.5 rounded-md text-[11px] font-medium border border-gray-300 text-gray-600 hover:bg-gray-100 transition-colors w-full justify-center"
                  >
                    <RotateCcw size={11} />
                    Reset to "{activeBuiltinPreset.name}"
                  </button>
                </div>
              )}

              {/* Save Custom Preset */}
              <div className="mt-3">
                {showSaveInput ? (
                  <div className="flex items-center gap-1.5">
                    <input
                      autoFocus
                      type="text"
                      value={newPresetName}
                      onChange={e => setNewPresetName(e.target.value)}
                      onKeyDown={e => {
                        if (e.key === "Enter" && newPresetName.trim()) {
                          saveCustomPreset(newPresetName.trim());
                          setNewPresetName("");
                          setShowSaveInput(false);
                        }
                        if (e.key === "Escape") {
                          setNewPresetName("");
                          setShowSaveInput(false);
                        }
                      }}
                      placeholder="Preset name..."
                      className="flex-1 text-[11px] px-2 py-1 border border-gray-300 rounded-md outline-none focus:border-indigo-400"
                      maxLength={30}
                    />
                    <button
                      onClick={() => {
                        if (newPresetName.trim()) {
                          saveCustomPreset(newPresetName.trim());
                          setNewPresetName("");
                          setShowSaveInput(false);
                        }
                      }}
                      disabled={!newPresetName.trim()}
                      className="px-2 py-1 rounded-md text-[11px] font-medium bg-indigo-500 text-white hover:bg-indigo-600 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                    >
                      Save
                    </button>
                    <button
                      onClick={() => {
                        setNewPresetName("");
                        setShowSaveInput(false);
                      }}
                      className="px-2 py-1 rounded-md text-[11px] font-medium text-gray-500 hover:bg-gray-100 transition-colors"
                    >
                      Cancel
                    </button>
                  </div>
                ) : (
                  <button
                    onClick={() => setShowSaveInput(true)}
                    className="flex items-center gap-1.5 px-2 py-1 rounded-md text-[11px] font-medium border border-dashed border-gray-300 text-gray-500 hover:border-indigo-400 hover:text-indigo-600 hover:bg-indigo-50 transition-colors w-full justify-center"
                  >
                    <Plus size={11} />
                    Save Current as Custom Preset
                  </button>
                )}
              </div>

              {/* Export / Import Palette as JSON */}
              <div className="mt-3 flex items-center gap-2">
                <button
                  onClick={() => {
                    const json = JSON.stringify(colors, null, 2);
                    const blob = new Blob([json], { type: "application/json" });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement("a");
                    a.href = url;
                    a.download = `kiddiwear-palette-${Date.now()}.json`;
                    a.click();
                    URL.revokeObjectURL(url);
                  }}
                  className="flex items-center gap-1.5 px-2 py-1.5 rounded-md text-[11px] font-medium border border-gray-300 text-gray-600 hover:bg-gray-100 transition-colors flex-1 justify-center"
                  title="Export current palette as JSON file"
                >
                  <Download size={11} />
                  Export JSON
                </button>
                <label
                  className="flex items-center gap-1.5 px-2 py-1.5 rounded-md text-[11px] font-medium border border-gray-300 text-gray-600 hover:bg-gray-100 transition-colors flex-1 justify-center cursor-pointer"
                  title="Import palette from a JSON file"
                >
                  <Upload size={11} />
                  Import JSON
                  <input
                    type="file"
                    accept=".json,application/json"
                    className="hidden"
                    onChange={e => {
                      const file = e.target.files?.[0];
                      if (!file) return;
                      const reader = new FileReader();
                      reader.onload = ev => {
                        try {
                          const parsed = JSON.parse(
                            ev.target?.result as string
                          );
                          // Validate: must have at least some DS token keys
                          const validKeys = DS_TOKEN_KEYS.filter(
                            k =>
                              typeof parsed[k] === "string" &&
                              /^#[0-9A-Fa-f]{6}$/.test(parsed[k])
                          );
                          if (validKeys.length === 0) {
                            alert(
                              "Invalid palette file: no valid color tokens found."
                            );
                            return;
                          }
                          // Apply only valid keys
                          const partial: Record<string, string> = {};
                          for (const k of validKeys) {
                            partial[k] = parsed[k].toUpperCase();
                          }
                          setColors(partial);
                          setActivePresetId("");
                          showImportToast();
                        } catch {
                          alert(
                            "Failed to parse JSON file. Please check the format."
                          );
                        }
                      };
                      reader.readAsText(file);
                      // Reset input so same file can be re-imported
                      e.target.value = "";
                    }}
                  />
                </label>
              </div>
            </div>

            {/* Token groups + Contrast Checker */}
            <div className="overflow-y-auto flex-1 min-h-0">
              {/* Contrast Checker section — always at the top */}
              <div className="border-b border-gray-50">
                <button
                  onClick={() => toggleGroup("Contrast Checker")}
                  className="w-full flex items-center justify-between px-4 py-2.5 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center gap-2">
                    <span className="text-[11px] font-semibold uppercase tracking-wider text-gray-500">
                      Contrast Checker
                    </span>
                    {/* Summary badge */}
                    <span className="inline-flex items-center gap-1">
                      <span
                        className="text-[9px] font-bold px-1.5 py-0.5 rounded"
                        style={{
                          background:
                            contrastSummary.fail === 0 ? "#D1FAE5" : "#FEE2E2",
                          color:
                            contrastSummary.fail === 0 ? "#065F46" : "#991B1B",
                        }}
                      >
                        {contrastSummary.fail === 0
                          ? `${contrastSummary.pass}/${contrastSummary.total} Pass`
                          : `${contrastSummary.fail} Fail`}
                      </span>
                    </span>
                  </div>
                  {expandedGroups["Contrast Checker"] ? (
                    <ChevronUp size={12} className="text-gray-400" />
                  ) : (
                    <ChevronDown size={12} className="text-gray-400" />
                  )}
                </button>
                {expandedGroups["Contrast Checker"] && (
                  <div className="px-4 pb-3">
                    <p className="text-[9px] text-gray-400 mb-2">
                      WCAG 2.1 — AA requires 4.5:1 (normal text), AAA requires
                      7:1
                    </p>
                    {CONTRAST_PAIRS.map(pair => (
                      <ContrastPairRow
                        key={`${pair.bg}-${pair.fg}`}
                        pair={pair}
                        colors={colors as unknown as Record<string, string>}
                      />
                    ))}
                  </div>
                )}
              </div>

              {TOKEN_GROUPS.map(group => {
                // Compute WCAG failures for this section
                const sectionPairs = CONTRAST_PAIRS.filter(pair =>
                  group.tokens.some(t => t.key === pair.bg || t.key === pair.fg)
                );
                const sectionFails = sectionPairs.filter(pair => {
                  const bgHex =
                    (colors as unknown as Record<string, string>)[pair.bg] ||
                    "#FFFFFF";
                  const fgHex =
                    (colors as unknown as Record<string, string>)[pair.fg] ||
                    "#000000";
                  return getWCAGLevel(contrastRatio(bgHex, fgHex)) === "FAIL";
                }).length;

                return (
                  <div
                    key={group.label}
                    className="border-b border-gray-50 last:border-b-0"
                  >
                    <button
                      onClick={() => toggleGroup(group.label)}
                      className="w-full flex items-center justify-between px-4 py-2.5 hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex items-center gap-2">
                        <span className="text-[11px] font-semibold uppercase tracking-wider text-gray-500">
                          {group.label}
                        </span>
                        {sectionPairs.length > 0 && (
                          <span
                            className="text-[9px] font-bold px-1.5 py-0.5 rounded"
                            style={{
                              background:
                                sectionFails === 0 ? "#D1FAE5" : "#FEE2E2",
                              color: sectionFails === 0 ? "#065F46" : "#991B1B",
                            }}
                          >
                            {sectionFails === 0
                              ? `${sectionPairs.length}/${sectionPairs.length} Pass`
                              : `${sectionFails} Fail`}
                          </span>
                        )}
                      </div>
                      {expandedGroups[group.label] ? (
                        <ChevronUp size={12} className="text-gray-400" />
                      ) : (
                        <ChevronDown size={12} className="text-gray-400" />
                      )}
                    </button>
                    {expandedGroups[group.label] && (
                      <div className="px-4 pb-3">
                        {group.tokens.map(token => {
                          // Find failing contrast pairs involving this token
                          const tokenFailingPairs = CONTRAST_PAIRS.filter(
                            pair =>
                              pair.bg === token.key || pair.fg === token.key
                          )
                            .map(pair => {
                              const bgHex =
                                (colors as unknown as Record<string, string>)[
                                  pair.bg
                                ] || "#FFFFFF";
                              const fgHex =
                                (colors as unknown as Record<string, string>)[
                                  pair.fg
                                ] || "#000000";
                              const ratio = contrastRatio(bgHex, fgHex);
                              const level = getWCAGLevel(ratio);
                              return { label: pair.label, ratio, level };
                            })
                            .filter(r => r.level === "FAIL");
                          return (
                            <ColorSwatch
                              key={token.key}
                              colorKey={token.key}
                              label={token.label}
                              activePresetColors={activePresetColors}
                              failingPairs={
                                tokenFailingPairs.length > 0
                                  ? tokenFailingPairs
                                  : undefined
                              }
                            />
                          );
                        })}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </>
  );
}
