"use client"

import { motion } from "framer-motion"

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@sprint-sync/ui"
import { fadeInUp, staggerContainer } from "@sprint-sync/ui/lib/animation"

const faqs = [
  {
    question: "How is SprintSync different from other project management tools?",
    answer:
      "SprintSync is designed for fast, disciplined product teams. It combines the speed of Linear, the financial-grade security of Stripe, and the polish of Vercel into a single, opinionated workspace.",
  },
  {
    question: "Can I import my existing boards and issues?",
    answer:
      "Yes. SprintSync includes importers for Jira, Asana, Trello, Linear, and GitHub Issues, plus a flexible CSV import for everything else.",
  },
  {
    question: "Is SprintSync secure enough for an enterprise?",
    answer:
      "Absolutely. SprintSync ships with SSO, SCIM, audit logs, role-based access control, and SOC 2 Type II compliance.",
  },
  {
    question: "Do you support on-premise or private cloud deployments?",
    answer:
      "Yes. We offer single-tenant cloud and Kubernetes deployments for organizations that need complete control over their data.",
  },
  {
    question: "What does the free plan include?",
    answer:
      "The free plan includes unlimited personal projects, up to three workspaces, and full access to core task and sprint features.",
  },
]

export function FAQ() {
  return (
    <section id="faq" className="bg-background py-24 md:py-32">
      <div className="container max-w-3xl">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={staggerContainer}
          className="text-center"
        >
          <motion.h2 variants={fadeInUp} className="text-h2 text-foreground">
            Frequently asked questions.
          </motion.h2>
          <motion.p
            variants={fadeInUp}
            className="mt-4 text-lg text-muted-foreground"
          >
            Everything you need to know before getting started.
          </motion.p>
        </motion.div>

        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={staggerContainer}
          className="mt-16"
        >
          <Accordion type="single" collapsible className="w-full">
            {faqs.map((item, index) => (
              <motion.div key={item.question} variants={fadeInUp}>
                <AccordionItem value={`item-${index}`}>
                  <AccordionTrigger className="text-left text-foreground">
                    {item.question}
                  </AccordionTrigger>
                  <AccordionContent className="text-muted-foreground">
                    {item.answer}
                  </AccordionContent>
                </AccordionItem>
              </motion.div>
            ))}
          </Accordion>
        </motion.div>
      </div>
    </section>
  )
}
