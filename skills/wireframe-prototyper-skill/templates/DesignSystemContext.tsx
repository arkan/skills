import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
} from "react";

/* ─── M3 Design System Token Keys (matching screenshot) ─── */
export const DS_TOKEN_KEYS = [
  // Primary
  "primary",
  "onPrimary",
  "primaryContainer",
  "onPrimaryContainer",
  // Secondary
  "secondary",
  "onSecondary",
  "secondaryContainer",
  "onSecondaryContainer",
  // Tertiary
  "tertiary",
  "onTertiary",
  "tertiaryContainer",
  "onTertiaryContainer",
  // Success
  "success",
  "onSuccess",
  "successContainer",
  "onSuccessContainer",
  // Error
  "error",
  "onError",
  "errorContainer",
  "onErrorContainer",
  // Surface
  "surface",
  "onSurface",
  "surfaceVariant",
  "onSurfaceVariant",
  "surfaceContainerHighest",
  "surfaceContainerHigh",
  "surfaceContainer",
  "surfaceContainerLow",
  "surfaceContainerLowest",
  "inverseSurface",
  "inverseOnSurface",
  "surfaceTint",
  "surfaceTintColor",
  // Outline
  "outline",
  "outlineVariant",
] as const;

export type DSColorKey = (typeof DS_TOKEN_KEYS)[number];
export type DSColors = Record<DSColorKey, string>;

import { DS_PRESETS, DEFAULT_DS_COLORS } from "./dsPresets";
export { DS_PRESETS, DEFAULT_DS_COLORS } from "./dsPresets";

/* ─── CSS Variable mapping ─── */
const CSS_VAR_MAP: Record<DSColorKey, string> = {
  primary: "--ds-primary",
  onPrimary: "--ds-on-primary",
  primaryContainer: "--ds-primary-container",
  onPrimaryContainer: "--ds-on-primary-container",
  secondary: "--ds-secondary",
  onSecondary: "--ds-on-secondary",
  secondaryContainer: "--ds-secondary-container",
  onSecondaryContainer: "--ds-on-secondary-container",
  tertiary: "--ds-tertiary",
  onTertiary: "--ds-on-tertiary",
  tertiaryContainer: "--ds-tertiary-container",
  onTertiaryContainer: "--ds-on-tertiary-container",
  success: "--ds-success",
  onSuccess: "--ds-on-success",
  successContainer: "--ds-success-container",
  onSuccessContainer: "--ds-on-success-container",
  error: "--ds-error",
  onError: "--ds-on-error",
  errorContainer: "--ds-error-container",
  onErrorContainer: "--ds-on-error-container",
  surface: "--ds-surface",
  onSurface: "--ds-on-surface",
  surfaceVariant: "--ds-surface-variant",
  onSurfaceVariant: "--ds-on-surface-variant",
  surfaceContainerHighest: "--ds-surface-container-highest",
  surfaceContainerHigh: "--ds-surface-container-high",
  surfaceContainer: "--ds-surface-container",
  surfaceContainerLow: "--ds-surface-container-low",
  surfaceContainerLowest: "--ds-surface-container-lowest",
  inverseSurface: "--ds-inverse-surface",
  inverseOnSurface: "--ds-inverse-on-surface",
  surfaceTint: "--ds-surface-tint",
  surfaceTintColor: "--ds-surface-tint-color",
  outline: "--ds-outline",
  outlineVariant: "--ds-outline-variant",
};

const STORAGE_KEY = "kiddiwear-ds-colors-v3";
const CUSTOM_PRESETS_KEY = "kiddiwear-ds-custom-presets-v3";

export interface CustomPreset {
  id: string;
  name: string;
  colors: DSColors;
}

interface DesignSystemContextType {
  colors: DSColors;
  setColor: (key: DSColorKey, value: string) => void;
  setColors: (colors: Partial<DSColors>) => void;
  resetColors: () => void;
  customPresets: CustomPreset[];
  saveCustomPreset: (name: string) => void;
  updateCustomPreset: (id: string) => void;
  renameCustomPreset: (id: string, newName: string) => void;
  deleteCustomPreset: (id: string) => void;
  activePresetId: string | null;
  setActivePresetId: (id: string | null) => void;
}

const DesignSystemContext = createContext<DesignSystemContextType | undefined>(
  undefined
);

export function DesignSystemProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [colors, setColorsState] = useState<DSColors>(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        return { ...DEFAULT_DS_COLORS, ...parsed };
      }
    } catch {}
    return { ...DEFAULT_DS_COLORS };
  });

  const [customPresets, setCustomPresets] = useState<CustomPreset[]>(() => {
    try {
      const stored = localStorage.getItem(CUSTOM_PRESETS_KEY);
      if (stored) return JSON.parse(stored);
    } catch {}
    return [];
  });

  const [activePresetId, setActivePresetId] = useState<string | null>(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY + "-active-preset");
      if (stored) return stored;
    } catch {}
    return "Terracotta & Gold";
  });

  /* Persist active preset id */
  useEffect(() => {
    if (activePresetId) {
      localStorage.setItem(STORAGE_KEY + "-active-preset", activePresetId);
    } else {
      localStorage.removeItem(STORAGE_KEY + "-active-preset");
    }
  }, [activePresetId]);

  /* Inject CSS variables into the document root whenever colors change */
  useEffect(() => {
    const root = document.documentElement;
    for (const key of DS_TOKEN_KEYS) {
      root.style.setProperty(CSS_VAR_MAP[key], colors[key]);
    }
    // Derived shadow variables
    const r = parseInt(colors.primary.slice(1, 3), 16);
    const g = parseInt(colors.primary.slice(3, 5), 16);
    const b = parseInt(colors.primary.slice(5, 7), 16);
    root.style.setProperty("--ds-shadow", `0 2px 8px rgba(0,0,0,0.08)`);
    root.style.setProperty("--ds-shadow-md", `0 4px 16px rgba(0,0,0,0.12)`);
    root.style.setProperty(
      "--ds-focus-ring",
      `0 0 0 3px rgba(${r},${g},${b},0.15)`
    );
  }, [colors]);

  /* Persist to localStorage */
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(colors));
  }, [colors]);

  /* Persist custom presets to localStorage */
  useEffect(() => {
    localStorage.setItem(CUSTOM_PRESETS_KEY, JSON.stringify(customPresets));
  }, [customPresets]);

  const setColor = useCallback((key: DSColorKey, value: string) => {
    setColorsState(prev => ({ ...prev, [key]: value }));
  }, []);

  const setColors = useCallback((partial: Partial<DSColors>) => {
    setColorsState(prev => ({ ...prev, ...partial }));
  }, []);

  const resetColors = useCallback(() => {
    setColorsState({ ...DEFAULT_DS_COLORS });
    localStorage.removeItem(STORAGE_KEY);
  }, []);

  const saveCustomPreset = useCallback(
    (name: string) => {
      const newPreset: CustomPreset = {
        id: `custom-${Date.now()}`,
        name,
        colors: { ...colors },
      };
      setCustomPresets(prev => [...prev, newPreset]);
      setActivePresetId(newPreset.id);
    },
    [colors]
  );

  const updateCustomPreset = useCallback(
    (id: string) => {
      setCustomPresets(prev =>
        prev.map(p => (p.id === id ? { ...p, colors: { ...colors } } : p))
      );
    },
    [colors]
  );

  const renameCustomPreset = useCallback((id: string, newName: string) => {
    setCustomPresets(prev =>
      prev.map(p => (p.id === id ? { ...p, name: newName } : p))
    );
  }, []);

  const deleteCustomPreset = useCallback((id: string) => {
    setCustomPresets(prev => prev.filter(p => p.id !== id));
  }, []);

  return (
    <DesignSystemContext.Provider
      value={{
        colors,
        setColor,
        setColors,
        resetColors,
        customPresets,
        saveCustomPreset,
        updateCustomPreset,
        renameCustomPreset,
        deleteCustomPreset,
        activePresetId,
        setActivePresetId,
      }}
    >
      {children}
    </DesignSystemContext.Provider>
  );
}

export function useDesignSystem() {
  const context = useContext(DesignSystemContext);
  if (!context) {
    throw new Error("useDesignSystem must be used within DesignSystemProvider");
  }
  return context;
}
