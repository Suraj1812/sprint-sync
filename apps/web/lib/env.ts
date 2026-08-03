import { clientEnvSchema } from "@sprint-sync/validation"

export const clientEnv = clientEnvSchema.parse(process.env)
