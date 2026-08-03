"use client"

import { motion } from "framer-motion"
import { Quote } from "lucide-react"

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Avatar,
  AvatarFallback,
} from "@sprint-sync/ui"
import { fadeIn, staggerContainer } from "@sprint-sync/ui/lib/animation"

const companies = [
  "Vercel",
  "Stripe",
  "Linear",
  "Notion",
  "Framer",
  "Raycast",
]

const testimonials = [
  {
    quote:
      "SprintSync turned our chaotic release process into a predictable, delightful workflow.",
    author: "Jane Doe",
    role: "VP of Product, Vercel",
    initials: "JD",
  },
  {
    quote:
      "The fastest tool we have ever rolled out. The design system alone saved us months.",
    author: "Alex Lee",
    role: "Engineering Lead, Linear",
    initials: "AL",
  },
  {
    quote:
      "Finally, a project management platform that feels as premium as the products we ship.",
    author: "Maria Kim",
    role: "Design Director, Framer",
    initials: "MK",
  },
]

export function SocialProof() {
  return (
    <section className="border-b border-border bg-surface py-20">
      <div className="container">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={staggerContainer}
          className="text-center"
        >
          <motion.p
            variants={fadeIn}
            className="text-sm font-medium text-muted-foreground"
          >
            Trusted by teams at
          </motion.p>
          <motion.div
            variants={fadeIn}
            className="mt-6 flex flex-wrap items-center justify-center gap-8 md:gap-12"
          >
            {companies.map((company) => (
              <span
                key={company}
                className="text-lg font-semibold text-muted-foreground/60"
              >
                {company}
              </span>
            ))}
          </motion.div>
        </motion.div>

        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={staggerContainer}
          className="mt-20 grid gap-6 md:grid-cols-2 lg:grid-cols-3"
        >
          {testimonials.map((item) => (
            <motion.div key={item.author} variants={fadeIn}>
              <Card className="h-full">
                <CardHeader>
                  <Quote className="h-6 w-6 text-muted-foreground" />
                </CardHeader>
                <CardContent className="pt-0">
                  <p className="text-foreground">{item.quote}</p>
                  <div className="mt-6 flex items-center gap-3">
                    <Avatar>
                      <AvatarFallback>{item.initials}</AvatarFallback>
                    </Avatar>
                    <div>
                      <CardTitle className="text-base">{item.author}</CardTitle>
                      <CardDescription>{item.role}</CardDescription>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
