"use client"

import Image from "next/image"
import { motion } from "framer-motion"
import { ArrowRight, Play, Star } from "lucide-react"

import { Button, Avatar, AvatarFallback } from "@sprint-sync/ui"
import { fadeInUp, staggerContainer } from "@sprint-sync/ui/lib/animation"

const avatars = ["JD", "AL", "MK", "SR"]

export function Hero() {
  return (
    <section
      id="hero"
      className="relative overflow-hidden border-b border-border/40 bg-background"
      aria-labelledby="hero-heading"
    >
      <div className="container py-24 md:py-32 lg:py-40">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={staggerContainer}
          className="grid gap-12 lg:grid-cols-2 lg:gap-16 items-center"
        >
          <div className="max-w-2xl">
            <motion.h1
              id="hero-heading"
              variants={fadeInUp}
              className="text-hero text-foreground"
            >
              Ship better products, faster.
            </motion.h1>
            <motion.p
              variants={fadeInUp}
              className="mt-6 text-lg text-muted-foreground md:text-xl"
            >
              SprintSync brings the clarity of Linear, the polish of Stripe, and
              the speed of Vercel to agile project management.
            </motion.p>
            <motion.div
              variants={fadeInUp}
              className="mt-8 flex flex-col gap-3 sm:flex-row"
            >
              <Button asChild size="lg" className="w-full sm:w-auto">
                <a href="#cta">
                  Start for free <ArrowRight className="ml-2 h-4 w-4" />
                </a>
              </Button>
              <Button
                asChild
                variant="outline"
                size="lg"
                className="w-full sm:w-auto"
              >
                <a href="#product">
                  <Play className="mr-2 h-4 w-4" /> Watch demo
                </a>
              </Button>
            </motion.div>
            <motion.div
              variants={fadeInUp}
              className="mt-10 flex flex-wrap items-center gap-4"
            >
              <div className="flex -space-x-2" aria-hidden="true">
                {avatars.map((initials) => (
                  <Avatar key={initials} className="border-2 border-background">
                    <AvatarFallback>{initials}</AvatarFallback>
                  </Avatar>
                ))}
              </div>
              <div>
                <div className="flex items-center gap-1">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <Star
                      key={i}
                      className="h-4 w-4 fill-warning text-warning"
                    />
                  ))}
                </div>
                <p className="mt-1 text-sm text-muted-foreground">
                  Loved by 2,000+ product teams
                </p>
              </div>
            </motion.div>
          </div>

          <motion.div
            variants={fadeInUp}
            className="relative rounded-2xl border border-border bg-surface p-2 shadow-card"
          >
            <Image
              src="/hero-dashboard.svg"
              alt="SprintSync dashboard preview showing sprint velocity, task board, and team activity"
              width={920}
              height={640}
              priority
              className="rounded-xl"
            />
          </motion.div>
        </motion.div>
      </div>
    </section>
  )
}
