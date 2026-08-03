"use client"

import { motion } from "framer-motion"
import { ArrowRight } from "lucide-react"

import { Button } from "@sprint-sync/ui"
import { fadeInUp, staggerContainer } from "@sprint-sync/ui/lib/animation"

export function CTA() {
  return (
    <section
      id="cta"
      className="bg-background py-24 md:py-32"
    >
      <div className="container">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={staggerContainer}
          className="relative overflow-hidden rounded-3xl border border-border bg-surface px-6 py-16 text-center shadow-card md:px-12 md:py-24"
        >
          <motion.h2
            variants={fadeInUp}
            className="text-h2 mx-auto max-w-2xl text-foreground"
          >
            Ready to ship your best work?
          </motion.h2>
          <motion.p
            variants={fadeInUp}
            className="mx-auto mt-4 max-w-xl text-lg text-muted-foreground"
          >
            Join thousands of product teams who have replaced chaos with
            clarity. Start for free, no credit card required.
          </motion.p>
          <motion.div
            variants={fadeInUp}
            className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row"
          >
            <Button asChild size="lg" className="w-full sm:w-auto">
              <a href="#">
                Start free trial <ArrowRight className="ml-2 h-4 w-4" />
              </a>
            </Button>
            <Button
              asChild
              variant="outline"
              size="lg"
              className="w-full sm:w-auto"
            >
              <a href="#product">See the product</a>
            </Button>
          </motion.div>
          <motion.p
            variants={fadeInUp}
            className="mt-4 text-sm text-muted-foreground"
          >
            Free 14-day trial. Cancel anytime.
          </motion.p>
        </motion.div>
      </div>
    </section>
  )
}
