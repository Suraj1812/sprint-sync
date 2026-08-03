import { Metadata } from "next"

import { Nav } from "./components/nav"
import { Footer } from "./components/footer"
import { StructuredData } from "./components/structured-data"
import { Hero } from "./sections/hero"
import { SocialProof } from "./sections/social-proof"
import { Features } from "./sections/features"
import { ProductShowcase } from "./sections/product-showcase"
import { Benefits } from "./sections/benefits"
import { Metrics } from "./sections/metrics"
import { FAQ } from "./sections/faq"
import { CTA } from "./sections/cta"

export const metadata: Metadata = {
  title: "SprintSync — Enterprise agile project management",
  description:
    "Ship better products, faster with SprintSync. The premium project management platform for fast-moving product teams.",
  keywords: [
    "agile",
    "sprint",
    "project management",
    "productivity",
    "kanban",
  ],
  openGraph: {
    title: "SprintSync — Enterprise agile project management",
    description: "Ship better products, faster with SprintSync.",
    type: "website",
    url: "https://sprintsync.dev",
    siteName: "SprintSync",
  },
  twitter: {
    card: "summary_large_image",
    title: "SprintSync — Enterprise agile project management",
    description: "Ship better products, faster with SprintSync.",
  },
  alternates: {
    canonical: "https://sprintsync.dev",
  },
  robots: {
    index: true,
    follow: true,
  },
}

export default function HomePage() {
  return (
    <>
      <StructuredData />
      <Nav />
      <main id="main" tabIndex={-1}>
        <Hero />
        <SocialProof />
        <Features />
        <ProductShowcase />
        <Benefits />
        <Metrics />
        <FAQ />
        <CTA />
      </main>
      <Footer />
    </>
  )
}
