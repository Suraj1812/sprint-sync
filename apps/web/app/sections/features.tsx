"use client"

import { motion } from "framer-motion"
import {
  Kanban,
  Zap,
  Shield,
  Users,
  BarChart3,
  Clock,
} from "lucide-react"

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@sprint-sync/ui"
import { fadeInUp, staggerContainer } from "@sprint-sync/ui/lib/animation"

const features = [
  {
    icon: Kanban,
    title: "Kanban & Sprints",
    description:
      "Plan, prioritize, and run sprints with a board that stays fast at any scale.",
  },
  {
    icon: Zap,
    title: "Real-time Sync",
    description:
      "See updates instantly across the entire team with WebSocket-powered live states.",
  },
  {
    icon: Shield,
    title: "Enterprise Security",
    description:
      "SSO, SCIM, audit logs, and RBAC built in from day one.",
  },
  {
    icon: Users,
    title: "Team Workspaces",
    description:
      "Organize work by organization, team, or project with clean access control.",
  },
  {
    icon: BarChart3,
    title: "Velocity Insights",
    description:
      "Track throughput, cycle time, and burndown without writing a single query.",
  },
  {
    icon: Clock,
    title: "Automation",
    description:
      "Eliminate busywork with rules that route work, set fields, and trigger alerts.",
  },
]

export function Features() {
  return (
    <section id="features" className="bg-background py-24 md:py-32">
      <div className="container">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={staggerContainer}
          className="mx-auto max-w-2xl text-center"
        >
          <motion.h2 variants={fadeInUp} className="text-h2 text-foreground">
            Everything your team needs to ship.
          </motion.h2>
          <motion.p
            variants={fadeInUp}
            className="mt-4 text-lg text-muted-foreground"
          >
            A complete toolkit for planning, tracking, and releasing great work.
          </motion.p>
        </motion.div>

        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={staggerContainer}
          className="mt-16 grid gap-6 sm:grid-cols-2 lg:grid-cols-3"
        >
          {features.map((feature) => (
            <motion.div key={feature.title} variants={fadeInUp}>
              <Card className="h-full transition-shadow hover:shadow-card">
                <CardHeader>
                  <feature.icon
                    className="h-8 w-8 text-primary"
                    aria-hidden="true"
                  />
                </CardHeader>
                <CardContent className="pt-0">
                  <CardTitle className="text-lg">{feature.title}</CardTitle>
                  <CardDescription className="mt-2">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
