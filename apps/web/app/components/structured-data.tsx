import Script from "next/script"

interface StructuredDataProps {
  nonce?: string
}

export function StructuredData({ nonce }: StructuredDataProps) {
  const data = {
    "@context": "https://schema.org",
    "@type": "WebSite",
    name: "SprintSync",
    url: "https://sprintsync.dev",
    description:
      "Enterprise-grade agile project management for fast-moving product teams.",
    publisher: {
      "@type": "Organization",
      name: "SprintSync",
    },
  }

  return (
    <Script
      id="json-ld"
      type="application/ld+json"
      strategy="beforeInteractive"
      nonce={nonce}
      dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }}
    />
  )
}
