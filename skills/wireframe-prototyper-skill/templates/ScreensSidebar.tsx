import { Link, useLocation } from "wouter";
import { Layout, ChevronRight } from "lucide-react";
import { useRef, useEffect } from "react";
import { useFidelityMode } from "@/contexts/FidelityModeContext";
import { screens } from "./screens";
import { PROJECT_NAME, PROJECT_INITIALS } from "./projectConfig";

interface ScreensSidebarProps {
  isOpen: boolean;
}

export default function ScreensSidebar({ isOpen }: ScreensSidebarProps) {
  const [location] = useLocation();
  const { isLofi, isMidfi } = useFidelityMode();
  const sidebarNavRef = useRef<HTMLElement>(null);
  const activeItemRef = useRef<HTMLAnchorElement>(null);

  /* Auto-scroll sidebar to active item */
  useEffect(() => {
    if (activeItemRef.current && sidebarNavRef.current) {
      activeItemRef.current.scrollIntoView({
        behavior: "smooth",
        block: "nearest",
      });
    }
  }, [location]);

  return (
    <aside
      className={`${
        isOpen ? "w-[270px]" : "w-0"
      } transition-all duration-300 ease-in-out flex-shrink-0 overflow-hidden`}
      style={{ background: "#1a1a2e", color: "#e0e0e0" }}
    >
      <div className="w-[270px] h-full flex flex-col">
        {/* Logo area */}
        <div
          className="px-5 py-5"
          style={{ borderBottom: "1px solid rgba(255,255,255,0.08)" }}
        >
          <div className="flex items-center gap-3">
            <div
              className="w-9 h-9 rounded-lg flex items-center justify-center"
              style={{
                background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
              }}
            >
              <span className="text-white text-sm font-bold">{PROJECT_INITIALS}</span>
            </div>
            <div>
              <h2 className="text-sm font-semibold text-white tracking-wide">
                {PROJECT_NAME}
              </h2>
              <p
                className="text-[10px] uppercase tracking-widest"
                style={{ color: "#8888aa" }}
              >
                Prototypes
              </p>
            </div>
          </div>
        </div>

        {/* Screen count badge */}
        <div className="px-5 pt-4 pb-2">
          <div className="flex items-center gap-2">
            <Layout size={12} style={{ color: "#8888aa" }} />
            <p
              className="text-[11px] font-medium uppercase tracking-wider"
              style={{ color: "#8888aa" }}
            >
              Screens
            </p>
            <span
              className="ml-auto text-[10px] font-semibold px-2 py-0.5 rounded-full"
              style={{ background: "rgba(99,102,241,0.2)", color: "#a5b4fc" }}
            >
              {screens.length}
            </span>
          </div>
        </div>

        {/* Navigation list */}
        <nav
          ref={sidebarNavRef}
          className="flex-1 overflow-y-auto px-3 py-1"
          style={{
            scrollbarWidth: "thin",
            scrollbarColor: "#333 transparent",
          }}
        >
          {screens.map((screen, i) => {
            const isActive = location === screen.path;
            return (
              <Link
                key={screen.path}
                to={screen.path}
                ref={isActive ? activeItemRef : undefined}
                className="flex items-center gap-3 px-3 py-2 rounded-lg text-[13px] transition-all duration-150 mb-0.5"
                style={{
                  background: isActive
                    ? "rgba(99,102,241,0.15)"
                    : "transparent",
                  color: isActive ? "#c7d2fe" : "#9999b0",
                  fontWeight: isActive ? 600 : 400,
                }}
              >
                <span
                  className="w-6 h-6 rounded-md flex items-center justify-center text-[11px] font-semibold flex-shrink-0"
                  style={{
                    background: isActive
                      ? "#6366f1"
                      : "rgba(255,255,255,0.06)",
                    color: isActive ? "#ffffff" : "#7777a0",
                  }}
                >
                  {i + 1}
                </span>
                <span className="truncate">{screen.label}</span>
                {isActive && (
                  <ChevronRight
                    size={14}
                    className="ml-auto flex-shrink-0"
                    style={{ color: "#6366f1" }}
                  />
                )}
              </Link>
            );
          })}
        </nav>

        {/* Footer */}
        <div
          className="px-5 py-4"
          style={{ borderTop: "1px solid rgba(255,255,255,0.06)" }}
        >
          <p className="text-[10px] text-center" style={{ color: "#5a5a7a" }}>
            {isLofi ? "Lo-fi" : isMidfi ? "Mid-fi" : "Hi-fi"} prototypes
            &middot; Desktop
          </p>
        </div>
      </div>
    </aside>
  );
}
