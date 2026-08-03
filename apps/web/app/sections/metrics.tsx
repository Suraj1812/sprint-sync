"use client"

import { motion, useInView, useMotionValue, useSpring } from "framer-motion"
import * as React from "react"

import { fadeInUp, staggerContainer } from "@sprint-sync/ui/lib/animation"

const metrics = [
  { label: "Teams onboarded", value: 2000, suffix: "+" },
  { label: "Tasks shipped weekly", value: 12, suffix: "M" },
  { label: "Average cycle time reduction", value: 34, suffix: "%" },
  { label: "Customer satisfaction", value: 99, suffix: "%" },
]

function AnimatedNumber({ value, suffix }: { value: number; suffix: string }) {
  const ref = React.useRef<HTMLSpanElement>(null)
  const motionValue = useMotionValue(0)
  const springValue = useSpring(motionValue, {
    damping: 50,
    stiffness: 100,
  })
  const isInView = useInView(ref, { once: true, margin: "-100px" })

  React.useEffect(() => {
    if (isInView) {
      motionValue.set(value)
    }
  }, [isInView, motionValue, value])

  React.useEffect(() => {
    const unsubscribe = springValue.on("change", (latest) => {
      if (ref.current) {
        ref.current.textContent = `${Math.floor(latest).toLocaleString()}${suffix}`
      }
    })
    return unsubscribe
  }, [springValue, suffix])

  return <span ref={ref} aria-live="polite" />
}

export function Metrics() {
  return (
    <section className="border-y border-border bg-surface py-24 md:py-32">
      <div className="container">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={staggerContainer}
          className="mx-auto max-w-2xl text-center"
        >
          <motion.h2 variants={fadeInUp} className="text-h2 text-foreground">
            Built for performance at scale.
          </motion.h2>
          <motion.p
            variants={fadeInUp}
            className="mt-4 text-lg text-muted-foreground"
          >
            Numbers from teams already using SprintSync.
          </motion.p>
        </motion.div>

        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={staggerContainer}
          className="mt-16 grid gap-8 sm:grid-cols-2 lg:grid-cols-4"
        >
          {metrics.map((metric) => (
            <motion.div
              key={metric.label}
              variants={fadeInUp}
              className="text-center"
            >
              <div className="text-display text-foreground">
                <AnimatedNumber value={metric.value} suffix={metric.suffix} />
              </div>
              <p className="mt-2 text-sm text-muted-foreground">
                {metric.label}
              </p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
