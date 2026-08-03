import type { Metadata, Viewport } from "next"
import { headers } from "next/headers"
import { Inter, JetBrains_Mono } from "next/font/google"

import { Providers } from "./providers"
import { StructuredData } from "./components/structured-data"
import "@sprint-sync/ui/styles/theme.css"
import "./globals.css"

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
  display: "swap",
})

const jetbrains = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  display: "swap",
})

export const metadata: Metadata = {
  metadataBase: new URL("https://sprintsync.dev"),
  title: { default: "SprintSync", template: "%s | SprintSync" },
  description:
    "Enterprise-grade agile project management for fast-moving product teams.",
  keywords: ["agile", "sprint", "project management", "productivity", "kanban"],
  openGraph: {
    title: "SprintSync",
    description: "Enterprise-grade agile project management.",
    url: "/",
    siteName: "SprintSync",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "SprintSync",
    description: "Enterprise-grade agile project management.",
  },
  robots: {
    index: true,
    follow: true,
  },
}

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#ffffff" },
    { media: "(prefers-color-scheme: dark)", color: "#0f172a" },
  ],
}

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const h = await headers()
  const nonce = h.get("x-nonce") ?? undefined

  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={`${inter.variable} ${jetbrains.variable}`}
    >
      <body className="min-h-screen bg-background text-foreground antialiased font-sans">
        <a
          href="#main"
          className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-md focus:bg-primary focus:px-4 focus:py-2 focus:text-primary-foreground"
        >
          Skip to content
        </a>
        <Providers>{children}</Providers>
        <StructuredData nonce={nonce} />
      </body>
    </html>
  )
}
