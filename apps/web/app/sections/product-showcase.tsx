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
            className="rounded-2xl border border-border bg-background p-2 shadow-card"
          >
            <Image
              src="/hero-dashboard.svg"
              alt="SprintSync product dashboard with sprint board, cycle time chart, and team member avatars"
              width={920}
              height={640}
              className="rounded-xl"
              loading="lazy"
            />
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
