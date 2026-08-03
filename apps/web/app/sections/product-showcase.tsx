"use client"

import Image from "next/image"
import { motion } from "framer-motion"
import { Check } from "lucide-react"

import { fadeIn, staggerContainer } from "@sprint-sync/ui/lib/animation"

const highlights = [
  "Real-time sprint boards",
  "Built-in cycle time analytics",
  "Team velocity at a glance",
  "One-click release notes",
]

export function ProductShowcase() {
  return (
    <section id="product" className="overflow-hidden bg-surface py-24 md:py-32">
      <div className="container">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={staggerContainer}
          className="grid gap-16 lg:grid-cols-2 items-center"
        >
          <motion.div
            variants={fadeIn}
            className="relative aspect-video w-full rounded-2xl border border-border bg-background p-2 shadow-card"
          >
            <div className="relative h-full w-full overflow-hidden rounded-xl">
              <Image
                src="https://images.unsplash.com/photo-1774600134168-b9ebd714e4e1?auto=format&fit=crop&w=920&q=80"
                alt="A real product team collaborating during a business presentation"
                fill
                className="object-cover"
                sizes="(max-width: 768px) 100vw, 50vw"
                loading="lazy"
              />
            </div>
          </motion.div>

          <div>
            <motion.h2
              variants={fadeIn}
              className="text-h2 text-foreground"
            >
              The clearest view of your work.
            </motion.h2>
            <motion.p
              variants={fadeIn}
              className="mt-4 text-lg text-muted-foreground"
            >
              A dashboard designed for focus. Surface blockers, track velocity,
              and keep everyone aligned without endless meetings.
            </motion.p>
            <motion.ul
              variants={staggerContainer}
              className="mt-8 space-y-4"
            >
              {highlights.map((item) => (
                <motion.li
                  key={item}
                  variants={fadeIn}
                  className="flex items-start gap-3"
                >
                  <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-success/10">
                    <Check className="h-4 w-4 text-success" />
                  </div>
                  <span className="text-foreground">{item}</span>
                </motion.li>
              ))}
            </motion.ul>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
