import type { Config } from "tailwindcss"

import { baseTailwindConfig } from "@sprint-sync/config/tailwind"

const config: Config = {
  ...baseTailwindConfig,
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "../../packages/ui/src/**/*.{js,ts,jsx,tsx,mdx}",
  ],
} as Config

export default config
