import { useFidelityMode } from "@/contexts/FidelityModeContext";
import { DS } from "@/contexts/DesignSystem";

/**
 * ImagePlaceholder — Renders differently based on fidelity mode.
 *
 * Lo-Fi: A rectangle with an X through it (crossbox) and an optional label.
 * Hi-Fi: A real image with DS border radius applied.
 *
 * Props:
 * - label: Descriptive text shown inside the crossbox (Lo-Fi only).
 * - className: Additional CSS classes for sizing and layout.
 * - aspectRatio: CSS aspect-ratio value (e.g. "16/9", "1/1", "3/4").
 * - src: Image URL for Hi-Fi mode. Required for Hi-Fi to display correctly.
 */
export function ImagePlaceholder({
  label = "Image",
  className = "",
  aspectRatio,
  src,
}: {
  label?: string;
  className?: string;
  aspectRatio?: string;
  src?: string;
}) {
  const { isLofi } = useFidelityMode();

  if (isLofi) {
    return (
      <div
        className={`relative overflow-hidden ${className}`}
        style={{
          border: "1px solid #000",
          borderRadius: 0,
          background: `
            linear-gradient(
              to top right,
              transparent calc(50% - 0.5px),
              #000 calc(50% - 0.5px),
              #000 calc(50% + 0.5px),
              transparent calc(50% + 0.5px)
            ),
            linear-gradient(
              to bottom right,
              transparent calc(50% - 0.5px),
              #000 calc(50% - 0.5px),
              #000 calc(50% + 0.5px),
              transparent calc(50% + 0.5px)
            )
          `,
          backgroundColor: "#fff",
          aspectRatio: aspectRatio || undefined,
          minHeight: "60px",
        }}
        data-label={label}
      />
    );
  }

  // Hi-Fi: real image
  return (
    <div
      className={`overflow-hidden ${className}`}
      style={{
        aspectRatio: aspectRatio || undefined,
        borderRadius: DS.radiusSm,
      }}
    >
      {src ? (
        <img
          src={src}
          alt={label}
          className="w-full h-full object-cover"
          loading="lazy"
        />
      ) : (
        <div
          className="w-full h-full flex items-center justify-center text-xs"
          style={{
            background: DS.surfaceContainerLow,
            color: DS.onSurfaceVariant,
            minHeight: "60px",
          }}
        >
          {label}
        </div>
      )}
    </div>
  );
}
