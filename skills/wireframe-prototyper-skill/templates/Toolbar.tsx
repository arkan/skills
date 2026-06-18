import { Link, useLocation } from "wouter";
import { Menu, X, Pencil, Maximize2, HelpCircle, Sparkles } from "lucide-react";
import { useFidelityMode } from "@/contexts/FidelityModeContext";
import ColorPaletteTool from "./ColorPaletteTool";
import { screens } from "./screens";

interface ToolbarProps {
  sidebarOpen: boolean;
  onToggleSidebar: () => void;
  containerSize: { w: number; h: number };
  onFullScreen: () => void;
  onShowHelp: () => void;
}

export default function Toolbar({
  sidebarOpen,
  onToggleSidebar,
  containerSize,
  onFullScreen,
  onShowHelp,
}: ToolbarProps) {
  const [location] = useLocation();
  const { mode, setMode, isLofi, isHifi, figmaCaptureMode, setFigmaCaptureMode } =
    useFidelityMode();

  const currentScreen = screens.find(s => s.path === location);
  const currentIndex = screens.findIndex(s => s.path === location);
  const prevScreen = currentIndex > 0 ? screens[currentIndex - 1] : null;
  const nextScreen = currentIndex < screens.length - 1 ? screens[currentIndex + 1] : null;

  return (
    <header
      className="h-14 flex items-center px-5 gap-4 flex-shrink-0"
      style={{
        background: "#ffffff",
        borderBottom: "1px solid #e5e5e5",
        boxShadow: "0 1px 3px rgba(0,0,0,0.04)",
      }}
    >
      <button
        onClick={onToggleSidebar}
        className="p-2 rounded-lg transition-colors duration-150"
        style={{ color: "#555", background: "transparent" }}
        onMouseEnter={e => (e.currentTarget.style.background = "#f0f0f0")}
        onMouseLeave={e => (e.currentTarget.style.background = "transparent")}
      >
        {sidebarOpen ? <X size={18} /> : <Menu size={18} />}
      </button>

      <div className="h-6 w-px" style={{ background: "#e0e0e0" }} />

      <div className="flex items-center gap-2">
        <span className="text-sm font-semibold" style={{ color: "#1a1a2e" }}>
          {currentScreen?.label || "Unknown Screen"}
        </span>
      </div>

      {/* Mode Toggle */}
      <div
        className="flex items-center gap-1 ml-6"
        style={{
          background: "#f3f4f6",
          borderRadius: "8px",
          padding: "3px",
        }}
      >
        <button
          onClick={() => setMode("lofi")}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all duration-200"
          style={{
            background: isLofi ? "#ffffff" : "transparent",
            color: isLofi ? "#6366f1" : "#888",
            boxShadow: isLofi ? "0 1px 3px rgba(0,0,0,0.1)" : "none",
          }}
        >
          <Pencil size={12} />
          Lo-Fi
        </button>

        <button
          onClick={() => setMode("hifi")}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all duration-200"
          style={{
            background: isHifi ? "#ffffff" : "transparent",
            color: isHifi ? "#6366f1" : "#888",
            boxShadow: isHifi ? "0 1px 3px rgba(0,0,0,0.1)" : "none",
          }}
        >
          <Sparkles size={12} />
          Hi-Fi
        </button>
      </div>

      <div className="ml-auto flex items-center gap-3">
        {/* Container Size */}
        {containerSize.w > 0 && (
          <span
            className="text-xs font-mono px-2 py-1 rounded"
            style={{ background: "#f3f4f6", color: "#666" }}
            title="Current container size (width × height)"
          >
            {containerSize.w} × {containerSize.h}
          </span>
        )}

        {/* Color Picker (Hi-Fi only) */}
        {isHifi && <ColorPaletteTool />}

        {isHifi && (
          <div className="h-5 w-px" style={{ background: "#e0e0e0" }} />
        )}

        {/* Figma Capture Mode toggle */}
        <button
          onClick={() => setFigmaCaptureMode(!figmaCaptureMode)}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-colors duration-150"
          style={{
            color: figmaCaptureMode ? "#6366f1" : "#666",
            background: figmaCaptureMode ? "#eef2ff" : "#f5f5f5",
          }}
          onMouseEnter={e =>
            (e.currentTarget.style.background = figmaCaptureMode
              ? "#e0e7ff"
              : "#eee")
          }
          onMouseLeave={e =>
            (e.currentTarget.style.background = figmaCaptureMode
              ? "#eef2ff"
              : "#f5f5f5")
          }
          title={
            figmaCaptureMode
              ? "Figma Capture Mode ON \u2014 dialogs won't auto-dismiss, background is clickable"
              : "Figma Capture Mode OFF"
          }
        >
          <svg
            width="13"
            height="13"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path d="M5 5.5A3.5 3.5 0 0 1 8.5 2H12v7H8.5A3.5 3.5 0 0 1 5 5.5Z" />
            <path d="M12 2h3.5A3.5 3.5 0 0 1 15.5 9H12V2Z" />
            <path d="M5 12a3.5 3.5 0 0 1 3.5-3.5H12v7H8.5A3.5 3.5 0 0 1 5 12Z" />
            <path d="M5 18.5A3.5 3.5 0 0 1 8.5 15H12v3.5a3.5 3.5 0 0 1-7 0Z" />
            <circle cx="15.5" cy="12" r="3.5" />
          </svg>
          {figmaCaptureMode ? "Figma Capture ON" : "Figma Capture"}
        </button>

        <div className="h-5 w-px" style={{ background: "#e0e0e0" }} />

        {/* Full Screen toggle */}
        <button
          onClick={onFullScreen}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-colors duration-150"
          style={{ color: "#666", background: "#f5f5f5" }}
          onMouseEnter={e => (e.currentTarget.style.background = "#eee")}
          onMouseLeave={e => (e.currentTarget.style.background = "#f5f5f5")}
          title="View wireframe in full screen"
        >
          <Maximize2 size={13} />
          Full Screen
        </button>

        <div className="h-5 w-px" style={{ background: "#e0e0e0" }} />

        {/* Help button */}
        <button
          onClick={onShowHelp}
          className="flex items-center justify-center w-7 h-7 rounded-md transition-colors duration-150"
          style={{ color: "#999", background: "transparent" }}
          onMouseEnter={e => {
            e.currentTarget.style.background = "#f0f0f0";
            e.currentTarget.style.color = "#666";
          }}
          onMouseLeave={e => {
            e.currentTarget.style.background = "transparent";
            e.currentTarget.style.color = "#999";
          }}
          title="Keyboard shortcuts (?)"
        >
          <HelpCircle size={16} />
        </button>

        <div className="h-5 w-px" style={{ background: "#e0e0e0" }} />

        {/* Prev / Next navigation */}
        {prevScreen && (
          <Link
            to={prevScreen.path}
            className="flex items-center gap-1 px-3 py-1.5 rounded-md text-xs font-medium transition-colors duration-150"
            style={{ color: "#666", background: "#f5f5f5" }}
          >
            &larr; Prev
          </Link>
        )}
        <span
          className="text-xs font-medium px-3 py-1.5 rounded-md"
          style={{ background: "#f0f0ff", color: "#6366f1" }}
        >
          {currentIndex + 1} / {screens.length}
        </span>
        {nextScreen && (
          <Link
            to={nextScreen.path}
            className="flex items-center gap-1 px-3 py-1.5 rounded-md text-xs font-medium transition-colors duration-150"
            style={{ color: "#666", background: "#f5f5f5" }}
          >
            Next &rarr;
          </Link>
        )}
      </div>
    </header>
  );
}
