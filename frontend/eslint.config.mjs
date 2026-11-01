import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  // Override default ignores of eslint-config-next.
  globalIgnores([
    // Default ignores of eslint-config-next:
    ".next/**",
    "out/**",
    "build/**",
    "next-env.d.ts",
  ]),
  // Project-level rule overrides
  {
    rules: {
      // Allow `any` type — common in rapid ML/healthcare prototypes
      "@typescript-eslint/no-explicit-any": "warn",
      // Allow unused vars as warnings, not errors
      "@typescript-eslint/no-unused-vars": "warn",
      // Allow unescaped entities (quotes inside JSX)
      "react/no-unescaped-entities": "warn",
      // Allow setState inside useEffect (used for client-only rendering guards)
      "react-hooks/exhaustive-deps": "warn",
    },
  },
]);

export default eslintConfig;
