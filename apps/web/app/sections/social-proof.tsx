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
  AvatarImage,
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
    src: "https://images.unsplash.com/photo-1762505464553-1f4eb1578f23?auto=format&fit=crop&w=80&h=80&crop=faces&q=80",
  },
  {
    quote:
      "The fastest tool we have ever rolled out. The design system alone saved us months.",
    author: "Alex Lee",
    role: "Engineering Lead, Linear",
    initials: "AL",
    src: "https://images.unsplash.com/photo-1758518729058-b158e71c5a9b?auto=format&fit=crop&w=80&h=80&crop=faces&q=80",
  },
  {
    quote:
      "Finally, a project management platform that feels as premium as the products we ship.",
    author: "Maria Kim",
    role: "Design Director, Framer",
    initials: "MK",
    src: "https://images.unsplash.com/photo-1758518727984-17b37f2f0562?auto=format&fit=crop&w=80&h=80&crop=faces&q=80",
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
                      <AvatarImage src={item.src} alt={item.author} />
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
