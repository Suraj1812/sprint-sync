import { z } from "zod"

export const clientEnvSchema = z.object({
  NEXT_PUBLIC_API_URL: z
    .string()
    .url()
    .default("http://localhost:8000"),
})

export type ClientEnv = z.infer<typeof clientEnvSchema>
