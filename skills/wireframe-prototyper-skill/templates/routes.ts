/**
 * Route constants — single source of truth for all path strings.
 * Import and reference by name instead of using string literals.
 */

// TODO: Update this object with all the project's route paths after defining the screen list
export const ROUTES = {
  HOME: "/",
} as const;

export type RoutePath = (typeof ROUTES)[keyof typeof ROUTES];
