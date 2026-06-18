import { useFidelityMode } from "@/contexts/FidelityModeContext";
import { DS } from "@/contexts/DesignSystem";

/**
 * TextPlaceholder — Renders differently based on fidelity mode.
 *
 * Lo-Fi: Black bars representing text lines (no readable content).
 * Hi-Fi: Real text content styled with DS colour tokens.
 *
 * Props:
 * - lines: Number of text lines to render. 1 = inline span, 2+ = block paragraph.
 * - width: Width of the single-line bar in Lo-Fi mode (e.g. "60%", "120px").
 * - className: Additional CSS classes for spacing and layout.
 * - text: The actual text content shown in Hi-Fi mode.
 */
export function TextPlaceholder({
  lines = 1,
  width = "60%",
  className = "",
  text,
}: {
  lines?: number;
  width?: string;
  className?: string;
  text?: string;
}) {
  const { isLofi } = useFidelityMode();

  // --- Single-line mode ---
  if (lines <= 1) {
    if (isLofi) {
      return (
        <span className={`wireframe-text-bar ${className}`} style={{ width }} />
      );
    }
    return (
      <span
        className={`text-sm ${className}`}
        style={{ color: DS.onSurfaceVariant }}
      >
        {text || "Placeholder text"}
      </span>
    );
  }

  // --- Multi-line mode ---
  if (isLofi) {
    const widths = ["100%", "92%", "78%", "65%", "92%", "100%", "78%", "65%"];
    return (
      <div className={`flex flex-col gap-1.5 ${className}`}>
        {Array.from({ length: lines }).map((_, i) => (
          <div
            key={i}
            className="wireframe-text-line"
            style={{ width: widths[i % widths.length] }}
          />
        ))}
      </div>
    );
  }

  // Hi-Fi: real paragraph text
  return (
    <div className={className}>
      <p
        className="text-sm leading-relaxed"
        style={{ color: DS.onSurfaceVariant }}
      >
        {text ||
          "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."}
      </p>
    </div>
  );
}
