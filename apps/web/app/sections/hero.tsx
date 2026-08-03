"use client"

import Image from "next/image"
import Link from "next/link"
import { motion } from "framer-motion"
import { ArrowRight, LogIn, Play, Star } from "lucide-react"

import { Button, Avatar, AvatarImage, AvatarFallback } from "@sprint-sync/ui"
import { fadeInUp, staggerContainer } from "@sprint-sync/ui/lib/animation"

const avatars = [
  {
    initials: "JD",
    src: "https://images.unsplash.com/photo-1762505464553-1f4eb1578f23?auto=format&fit=crop&w=80&h=80&crop=faces&q=80",
    name: "Jane Doe",
  },
  {
    initials: "AL",
    src: "https://images.unsplash.com/photo-1758518729058-b158e71c5a9b?auto=format&fit=crop&w=80&h=80&crop=faces&q=80",
    name: "Alex Lee",
  },
  {
    initials: "MK",
    src: "https://images.unsplash.com/photo-1758518727984-17b37f2f0562?auto=format&fit=crop&w=80&h=80&crop=faces&q=80",
    name: "Maria Kim",
  },
  {
    initials: "SR",
    src: "https://images.unsplash.com/photo-1758599543111-5db56cfa9a59?auto=format&fit=crop&w=80&h=80&crop=faces&q=80",
    name: "Sam Rivera",
  },
]

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
                <a
                  href="https://videos.pexels.com/video-files/3129671/3129671-sd_640_360_30fps.mp4"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <Play className="mr-2 h-4 w-4" /> Watch demo
                </a>
              </Button>
              <Button asChild variant="secondary" size="lg" className="w-full sm:w-auto">
                <Link href="/admin/login">
                  <LogIn className="mr-2 h-4 w-4" /> Sign in
                </Link>
              </Button>
            </motion.div>
            <motion.div
              variants={fadeInUp}
              className="mt-10 flex flex-wrap items-center gap-4"
            >
              <div className="flex -space-x-2" aria-hidden="true">
                {avatars.map((person) => (
                  <Avatar key={person.name} className="border-2 border-background">
                    <AvatarImage src={person.src} alt={person.name} />
                    <AvatarFallback>{person.initials}</AvatarFallback>
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
            className="relative aspect-video w-full rounded-2xl border border-border bg-surface p-2 shadow-card"
          >
            <div className="relative h-full w-full overflow-hidden rounded-xl">
              <Image
                src="https://images.unsplash.com/photo-1774600134168-b9ebd714e4e1?auto=format&fit=crop&w=920&q=80"
                alt="A real product team collaborating on laptops in a modern office"
                fill
                priority
                className="object-cover"
                sizes="(max-width: 768px) 100vw, 50vw"
              />
            </div>
          </motion.div>
        </motion.div>
      </div>
    </section>
  )
}
