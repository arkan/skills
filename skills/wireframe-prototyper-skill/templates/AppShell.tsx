import { useLocation } from "wouter";
import { X } from "lucide-react";
import { useState, useEffect, useRef } from "react";
import { useFidelityMode } from "@/contexts/FidelityModeContext";
import { useDSSync } from "@/contexts/DesignSystem";
import ScreensSidebar from "./ScreensSidebar";
import Toolbar from "./Toolbar";
import { screens } from "./screens";

export default function AppShell({ children }: { children: React.ReactNode }) {
  const [location, navigate] = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [fullScreen, setFullScreen] = useState(false);
  const [showHelp, setShowHelp] = useState(false);
  const [containerSize, setContainerSize] = useState<{ w: number; h: number }>({
    w: 0,
    h: 0,
  });
  const [fsSizeToastVisible, setFsSizeToastVisible] = useState(false);
  const fsSizeToastTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const fsToastPhaseRef = useRef<"idle" | "fade-in" | "visible" | "fade-out">(
    "idle"
  );
  const [fsToastOpacity, setFsToastOpacity] = useState(0);
  const fsToastTimers = useRef<ReturnType<typeof setTimeout>[]>([]);
  const { isLofi, isHifi, setMode } = useFidelityMode();
  useDSSync(); // Sync DS object with context colors on every render

  const currentIndex = screens.findIndex(s => s.path === location);

  /* ── Measure container size ── */
  useEffect(() => {
    if (!containerRef.current) return;
    const el = containerRef.current;
    const updateSize = () => {
      const w = Math.round(el.getBoundingClientRect().width);
      const h = Math.round(
        fullScreen ? el.scrollHeight : el.getBoundingClientRect().height
      );
      setContainerSize({ w, h });
    };
    const observer = new ResizeObserver(() => updateSize());
    observer.observe(el);
    if (fullScreen) {
      const mutObs = new MutationObserver(() => updateSize());
      mutObs.observe(el, { childList: true, subtree: true });
      updateSize();
      return () => {
        observer.disconnect();
        mutObs.disconnect();
      };
    }
    return () => observer.disconnect();
  }, [fullScreen]);

  /* ── Show size toast temporarily in full-screen on resize ── */
  useEffect(() => {
    if (!fullScreen) return;
    setFsSizeToastVisible(true);
    if (fsSizeToastTimer.current) clearTimeout(fsSizeToastTimer.current);
    fsSizeToastTimer.current = setTimeout(() => {
      setFsSizeToastVisible(false);
    }, 1500);
    return () => {
      if (fsSizeToastTimer.current) clearTimeout(fsSizeToastTimer.current);
    };
  }, [containerSize.w, containerSize.h, fullScreen]);

  /* ── Keyboard shortcuts ── */
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const tag = (e.target as HTMLElement)?.tagName;
      if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return;

      if (e.key === "Escape" && showHelp) {
        setShowHelp(false);
      } else if (e.key === "Escape" && fullScreen) {
        setFullScreen(false);
      } else if (e.key === "ArrowLeft" && currentIndex > 0) {
        navigate(screens[currentIndex - 1].path);
      } else if (e.key === "ArrowRight" && currentIndex < screens.length - 1) {
        navigate(screens[currentIndex + 1].path);
      } else if (e.key === "t" || e.key === "T") {
        setMode(isLofi ? "hifi" : "lofi");
      } else if (e.key === "f" || e.key === "F") {
        setFullScreen(prev => {
          if (!prev) showFsToast();
          return !prev;
        });
      } else if (e.key === "?") {
        setShowHelp(prev => !prev);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [fullScreen, showHelp, currentIndex, navigate, isLofi, isHifi, setMode]);

  /* ── Fullscreen toast helpers ── */
  const clearFsTimers = () => {
    fsToastTimers.current.forEach(clearTimeout);
    fsToastTimers.current = [];
  };
  const showFsToast = () => {
    clearFsTimers();
    fsToastPhaseRef.current = "idle";
    setFsToastOpacity(0);
    fsToastTimers.current.push(
      setTimeout(() => {
        fsToastPhaseRef.current = "fade-in";
        setFsToastOpacity(1);
      }, 50)
    );
    fsToastTimers.current.push(
      setTimeout(() => {
        fsToastPhaseRef.current = "fade-out";
        setFsToastOpacity(0);
      }, 2000)
    );
    fsToastTimers.current.push(
      setTimeout(() => {
        fsToastPhaseRef.current = "idle";
      }, 2500)
    );
  };
  useEffect(() => {
    return () => clearFsTimers();
  }, []);

  /* ── Help overlay ── */
  const helpOverlay = showHelp ? (
    <div
      className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/50"
      onClick={() => setShowHelp(false)}
    >
      <div
        className="bg-white rounded-lg shadow-2xl p-8 max-w-md w-full mx-4"
        onClick={e => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-bold text-gray-900">
            Keyboard Shortcuts
          </h2>
          <button
            onClick={() => setShowHelp(false)}
            className="text-gray-400 hover:text-gray-600"
          >
            <X size={20} />
          </button>
        </div>
        <div className="flex flex-col gap-3">
          {[
            { keys: ["←"], desc: "Previous screen" },
            { keys: ["→"], desc: "Next screen" },
            { keys: ["T"], desc: "Toggle Lo-Fi / Hi-Fi mode" },
            { keys: ["F"], desc: "Toggle full-screen mode" },
            { keys: ["Esc"], desc: "Exit full-screen or close overlay" },
            { keys: ["?"], desc: "Show / hide this help" },
          ].map(({ keys, desc }) => (
            <div key={desc} className="flex items-center justify-between">
              <span className="text-sm text-gray-600">{desc}</span>
              <div className="flex gap-1">
                {keys.map(k => (
                  <kbd
                    key={k}
                    className="inline-flex items-center justify-center min-w-[28px] h-7 px-2 bg-gray-100 border border-gray-300 rounded text-xs font-mono font-semibold text-gray-700"
                  >
                    {k}
                  </kbd>
                ))}
              </div>
            </div>
          ))}
        </div>
        <p className="mt-6 text-xs text-gray-400 text-center">
          Press{" "}
          <kbd className="px-1 py-0.5 bg-gray-100 border border-gray-300 rounded text-xs font-mono">
            ?
          </kbd>{" "}
          or{" "}
          <kbd className="px-1 py-0.5 bg-gray-100 border border-gray-300 rounded text-xs font-mono">
            Esc
          </kbd>{" "}
          to close
        </p>
      </div>
    </div>
  ) : null;

  /* ── Full-screen view ── */
  if (fullScreen) {
    return (
      <div
        ref={containerRef}
        className="h-screen w-screen overflow-auto bg-white"
      >
        {helpOverlay}
        <div className="fixed top-6 left-0 right-0 z-[9998] flex justify-center pointer-events-none">
          <div
            className="transition-all duration-500 ease-in-out"
            style={{
              opacity: fsToastOpacity,
              transform: `translateY(${fsToastOpacity ? "0" : "-12px"})`,
            }}
          >
            <div className="bg-gray-900/90 text-white text-sm px-5 py-3 rounded-lg shadow-lg flex items-center gap-2">
              Press{" "}
              <kbd className="inline-flex items-center justify-center min-w-[24px] h-6 px-1.5 bg-white/20 border border-white/30 rounded text-xs font-mono font-semibold">
                Esc
              </kbd>{" "}
              or{" "}
              <kbd className="inline-flex items-center justify-center min-w-[24px] h-6 px-1.5 bg-white/20 border border-white/30 rounded text-xs font-mono font-semibold">
                F
              </kbd>{" "}
              to exit full screen
            </div>
          </div>
        </div>
        {containerSize.w > 0 && (
          <div
            className="fixed bottom-6 left-0 right-0 z-[9998] flex justify-center pointer-events-none transition-opacity duration-300"
            style={{ opacity: fsSizeToastVisible ? 1 : 0 }}
          >
            <span className="text-xs font-mono px-3 py-1.5 rounded-lg shadow-lg bg-gray-900/90 text-white">
              {containerSize.w} × {containerSize.h}
            </span>
          </div>
        )}
        {children}
      </div>
    );
  }

  /* ── Normal shell view ── */
  return (
    <div
      className="shell-container flex h-screen"
      style={{ background: "#f5f5f5" }}
    >
      {helpOverlay}

      <ScreensSidebar isOpen={sidebarOpen} />

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <Toolbar
          sidebarOpen={sidebarOpen}
          onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
          containerSize={containerSize}
          onFullScreen={() => {
            setFullScreen(true);
            showFsToast();
          }}
          onShowHelp={() => setShowHelp(true)}
        />

        {/* Wireframe Canvas */}
        <main
          className="flex-1 overflow-auto p-6"
          style={{ background: "#f0f0f0" }}
        >
          <div
            ref={containerRef}
            className="max-w-[1200px] mx-auto bg-white min-h-[800px]"
            style={{
              border: "1px solid #000",
              boxShadow: "0 4px 24px rgba(0,0,0,0.08)",
            }}
          >
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
