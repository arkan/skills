# Wireframe Prototyper Skill

[Medium Article](https://medium.com/@elifsue/design-with-context-a-claude-skill-that-studies-competitors-and-builds-your-prototype-e4cdd8cb7519) | [YouTube Demo](https://www.youtube.com/watch?v=EIryl8x3PCI)

A Claude skill that builds interactive website wireframes and high-fidelity prototypes as deployed web applications. Instead of static mockups, you get a fully navigable prototype with switchable fidelity modes, a live colour system, and tools for presenting and exporting your work.

## What It Does

Give Claude a description of your project and this skill will produce a complete set of screens as a running web app. You can switch between Lo-Fi wireframes and Hi-Fi prototypes with a single click, change your entire colour palette in real time, and navigate between screens using a sidebar.

## Features

### Screen Navigation Sidebar

A numbered list of all screens in your project. Click any screen to navigate to it instantly. The sidebar shows the total screen count and highlights the currently active screen.

![Screen Navigation Sidebar](https://files.manuscdn.com/user_upload_by_module/session_file/310519663332337268/woByAOBAGBNhjAlA.gif)

### Dual-Fidelity Mode Switching

Toggle between two fidelity levels from the toolbar:

- **Lo-Fi** — Black and white wireframes with crossbox image placeholders, text represented as lines, no rounded corners, and no hover states. Pure structure.
- **Hi-Fi** — Full colour prototype using Material Design 3 tokens, generated images, hover states, border radius, elevation, and proper typography.

![Dual-Fidelity Mode Switching](https://files.manuscdn.com/user_upload_by_module/session_file/310519663332337268/zCvsuWgFVGZEYldm.gif)

### Colour Palette Tool

A built-in colour system editor that lets you:

- Swap between built-in presets (Terracotta & Gold, Ocean Breeze, Midnight Violet, Emerald Garden, Arctic Frost, Berry Dusk, Slate & Citrus) or your own custom palette.
- Edit individual M3 colour tokens with hex input or eyedropper.
- See changes reflected across all screens in real time.
- Check WCAG contrast ratios with per-swatch warning indicators for failing pairs.
- Save, rename, and delete custom presets.
- Export and import palettes as JSON.

![Colour Palette Tool](https://files.manuscdn.com/user_upload_by_module/session_file/310519663332337268/ORfRyRYFgzWnJezh.gif)

### Figma Capture Mode

A mode that prevents dialogs and dropdown menus from auto-dismissing when clicking outside them. This allows you to take screenshots of open dialogs and dropdowns without them closing. Designed for capturing every UI state cleanly so you can import the screenshots into Figma using Figma's Code to Canvas feature through Figma MCP.

![Figma Capture Mode](https://files.manuscdn.com/user_upload_by_module/session_file/310519663332337268/qNDSxczDzDITuSpu.gif)

### Full Screen Mode

Hides all UI chrome for stakeholder presentations. Toggle with the toolbar button or the `F` keyboard shortcut.

### Production-Ready Code

Every screen is built with proper React components, one component per file, using Tailwind CSS. The code is structured for reuse: design system components, contexts, hooks, and screens are all separated. The output is not throwaway wireframe code — it can serve as a foundation for production development.

## How to Use

### Step 1: Download the Skill

Download the `wireframe-prototyper-skill.zip` file from this repository.

### Step 2: Add It to Claude

Give the zip file to Claude as a skill. Once loaded, you can reference it in future conversations by its name.

### Step 3: Start a Conversation

Tell Claude what you want to prototype. For example:

> "I want to create wireframes for a second-hand children's clothing marketplace. Use the wireframe-prototyper skill."

### Step 4: Answer the Discovery Questions

The skill will ask you questions one at a time, like an interview:

1. **Fidelity scope** — Do you need Lo-Fi, Hi-Fi, or both?
2. **Competitor analysis** — Is there a similar website to draw inspiration from?
3. **Feature clarification** — Questions about specific features (authentication, messaging, payments, etc.)
4. **Screen list** — A suggested list of all screens, grouped by section. You can add, remove, or reorder.
5. **Project name** — A name for the prototype.
6. **Colour palette** — Your preferred colour style (warm, cool, earthy, vibrant, etc.)
7. **Typography** — A font family for the project.

### Step 5: Let It Build

Claude will set up the project, create design system components, and build each screen. The result is a deployed web app you can interact with immediately.

### Step 6: Iterate

Once the prototype is running, you can:

- Switch fidelity modes from the toolbar.
- Change colours using the Colour Palette Tool (no prompts needed, just click and pick).
- Ask Claude to modify specific screens or add new ones.
- Use Figma Capture Mode to screenshot screens for import into Figma.

## Built-In Presets

The skill ships with 7 colour palettes that all pass WCAG AA contrast requirements:

| Preset | Primary | Character |
|--------|---------|-----------|
| Terracotta & Gold | Warm terracotta | Earthy, organic |
| Ocean Breeze | Cool blue | Fresh, professional |
| Midnight Violet | Desaturated purple | Calm, creative |
| Emerald Garden | Rich green | Natural, grounded |
| Arctic Frost | Steel blue-grey | Minimal, technical |
| Berry Dusk | Magenta-berry | Bold, energetic |
| Slate & Citrus | Dark slate | Sharp, modern |

Your custom palette is always added as the first preset and becomes the default.

## File Structure

```
wireframe-prototyper-skill/
├── README.md                         ← This file
├── SKILL.md                          ← Main skill instructions
├── references/
│   ├── DESIGN_RULES_REFERENCE.md     ← Common rules for both fidelity modes
│   ├── HIGH_FIDELITY_PROTOTYPE_REFERENCE.md  ← Hi-Fi specific rules
│   ├── LOW_FIDELITY_WIREFRAME_REFERENCE.md   ← Lo-Fi specific rules
│   └── M3_COLOR_ROLES_REFERENCE.md   ← Material Design 3 colour system guide
└── templates/
    ├── AppShell.tsx                   ← Shell wrapper (sidebar + toolbar + canvas)
    ├── ColorPaletteTool.tsx           ← Colour system editor with WCAG checker
    ├── DesignSystem.ts               ← DS token object with live sync
    ├── DesignSystemContext.tsx        ← Colour state and preset management
    ├── dsPresets.ts                  ← Built-in palettes (add yours as first entry)
    ├── FidelityModeContext.tsx        ← Fidelity mode toggle context
    ├── ImagePlaceholder.tsx           ← Image placeholder (crossbox / real image)
    ├── projectConfig.ts              ← Project name & initials for sidebar logo
    ├── routes.ts                     ← Route constants (update with your routes)
    ├── screens.ts                    ← Screen definitions (update with your screens)
    ├── ScreensSidebar.tsx             ← Left sidebar with screen navigation
    ├── TextPlaceholder.tsx            ← Text placeholder (bars / real text)
    └── Toolbar.tsx                    ← Top toolbar with fidelity toggle and tools
```

## Requirements

- Claude with skill support
- A web development environment (the skill uses React, Tailwind CSS, and Vite)

## Workflow Overview

```
Discovery Questions → Project Setup → Design System Components → Screen Implementation → Compliance Verification
```

The skill enforces a compliance verification step at the end, checking every screen against the design rules, Hi-Fi requirements, and Lo-Fi requirements before delivering the final result.

## Competitive Analysis

If you provide a competitor website during discovery, the skill will browse it to understand layout patterns, navigation structure, and feature organisation. This structured inspiration helps produce screens that feel informed by real-world conventions rather than generic templates.

## Figma Integration

![Figma Integration](https://files.manuscdn.com/user_upload_by_module/session_file/310519663332337268/eniFvajlhqTqBnLC.png)

Use Figma Capture Mode to take clean screenshots of each screen, then import them into Figma using:

- **[Figma MCP](https://www.figma.com/mcp-catalog/)** — Send screenshots directly to Figma frames via the Model Context Protocol.
- **[Figma Code to Canvas](https://developers.figma.com/docs/figma-mcp-server/code-to-canvas/)** — Paste the component code into Figma's Code to Canvas feature to get editable Figma layers.

## License

MIT
