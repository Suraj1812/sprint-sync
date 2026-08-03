"use client"

import { motion } from "framer-motion"
import { Check, X } from "lucide-react"

import { Card, CardContent, CardTitle } from "@sprint-sync/ui"
import { fadeInUp, staggerContainer } from "@sprint-sync/ui/lib/animation"

const traditional = [
  "Scattered tools and spreadsheets",
  "Manual status updates",
  "Slow, overbuilt workflows",
  "Opaque progress reports",
]

const sprintsync = [
  "One source of truth for every team",
  "Live state, no refresh needed",
  "Opinionated, fast defaults",
  "Built-in analytics and insights",
]

export function Benefits() {
  return (
    <section id="benefits" className="bg-background py-24 md:py-32">
      <div className="container">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={staggerContainer}
          className="mx-auto max-w-2xl text-center"
        >
          <motion.h2 variants={fadeInUp} className="text-h2 text-foreground">
            Why teams choose SprintSync.
          </motion.h2>
          <motion.p
            variants={fadeInUp}
            className="mt-4 text-lg text-muted-foreground"
          >
            Less overhead. More clarity. Better releases.
          </motion.p>
        </motion.div>

        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={staggerContainer}
          className="mt-16 grid gap-8 md:grid-cols-2"
        >
          <motion.div variants={fadeInUp}>
            <Card className="h-full">
              <CardContent className="p-6">
                <CardTitle className="text-lg text-muted-foreground">
                  The old way
                </CardTitle>
                <ul className="mt-6 space-y-4">
                  {traditional.map((item) => (
                    <li key={item} className="flex items-start gap-3">
                      <X className="mt-0.5 h-4 w-4 shrink-0 text-destructive" />
                      <span className="text-muted-foreground">{item}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div variants={fadeInUp}>
            <Card className="h-full border-primary/20 bg-primary/5">
              <CardContent className="p-6">
                <CardTitle className="text-lg text-foreground">
                  With SprintSync
                </CardTitle>
                <ul className="mt-6 space-y-4">
                  {sprintsync.map((item) => (
                    <li key={item} className="flex items-start gap-3">
                      <Check className="mt-0.5 h-4 w-4 shrink-0 text-success" />
                      <span className="text-foreground">{item}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </motion.div>
        </motion.div>
      </div>
    </section>
  )
}
