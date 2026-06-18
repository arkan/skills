import {
  useDesignSystem,
  DSColors,
  DS_TOKEN_KEYS,
} from "./DesignSystemContext";
import { DEFAULT_DS_COLORS } from "./dsPresets";

/* ─── Design System Colors (Hi-Fi) ─── */
/* DS is a live mutable object synced by DesignSystemContext.
   Components that import DS and render inline styles will see
   updated values after the context triggers a re-render. */
const DS: DSColors & {
  radius: string;
  radiusSm: string;
  radiusLg: string;
  shadow: string;
  shadowMd: string;
} = {
  ...DEFAULT_DS_COLORS,
  // Non-color tokens (not editable via color picker)
  radius: "12px",
  radiusSm: "8px",
  radiusLg: "16px",
  shadow: "0 2px 8px rgba(0,0,0,0.08)",
  shadowMd: "0 4px 16px rgba(0,0,0,0.12)",
};

/* Hook that syncs the DS object with context values and forces re-render */
export function useDSSync() {
  const { colors } = useDesignSystem();
  // Mutate the DS object so all references see updated values
  for (const key of DS_TOKEN_KEYS) {
    (DS as any)[key] = colors[key];
  }
  // Recompute shadows from primary
  DS.shadow = `0 2px 8px rgba(0,0,0,0.08)`;
  DS.shadowMd = `0 4px 16px rgba(0,0,0,0.12)`;
  return colors;
}

export { DS };
