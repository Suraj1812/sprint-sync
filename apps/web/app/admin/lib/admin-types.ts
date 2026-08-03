export interface DashboardStats {
  total_users: number
  active_users: number
  new_registrations_24h: number
  failed_logins_24h: number
  admin_sessions: number
  pending_feature_flags: number
  uptime: string
  version: string
}

export interface AdminUser {
  id: string
  email: string
  first_name: string | null
  last_name: string | null
  is_active: boolean
  email_verified: boolean
  role: string
  last_login_at: string | null
  created_at: string
  updated_at: string
}

export interface FeatureFlag {
  id: string
  key: string
  name: string
  description: string | null
  enabled: boolean
  environment: string
  rollout_percentage: number
  targeting: Record<string, unknown> | null
  scheduled_at: string | null
  created_at: string
  updated_at: string
}

export interface AuditLog {
  id: string
  actor_id: string | null
  actor_email: string | null
  action: string
  resource: string
  resource_id: string | null
  ip_address: string | null
  created_at: string
}

export interface Prompt {
  id: string
  name: string
  description: string | null
  is_active: boolean
  default_version_id: string | null
  variables: string[]
  created_at: string
}

export interface UsageStats {
  total_cost_30d: number
  total_tokens_30d: number
}

export interface Provider {
  name: string
  ok: boolean
}

export interface SearchResult {
  id: string
  content: string
  score: number
  metadata: Record<string, unknown> | null
}

export interface Plan {
  id: string
  name: string
  description: string | null
  is_active: boolean
  is_enterprise: boolean
}

export interface Entitlement {
  id: string
  feature: string
  limit: number | null
  value: string | null
}

export interface Subscription {
  id: string
  customer_id: string
  plan_id: string
  price_id: string
  status: string
  current_period_end: string | null
  seats: number
}

export interface Invoice {
  id: string
  number: string | null
  status: string
  total: number
  paid: number
  pdf_url: string | null
  created_at: string
}

export interface BillingEvent {
  id: string
  provider: string
  event_type: string
  processed: boolean
  attempts: number
  created_at: string
}

export interface BillingMetrics {
  mrr: number
  arr: number
  active_subscriptions: number
  failed_payments_30d: number
}

export interface Organization {
  id: string
  name: string
  slug: string
  owner_id: string
  is_active: boolean
  billing_email: string | null
  created_at: string
}

export interface WorkspaceAdmin {
  id: string
  organization_id: string
  name: string
  slug: string
  is_archived: boolean
}

export interface InvitationAdmin {
  id: string
  organization_id: string
  email: string
  role: string
  expires_at: string
  accepted_at: string | null
  rejected_at: string | null
}

export interface EmailTemplate {
  id: string
  name: string
  locale: string
  version: number
  subject: string
  html_body: string | null
  text_body: string | null
  variables: string[]
  is_active: boolean
}

export interface DeliveryStats {
  total: number
  pending: number
  completed: number
  failed: number
  by_channel: Record<string, number>
}

export interface Workflow {
  id: string
  name: string
  description: string | null
  trigger: object
  steps: object[]
  is_active: boolean
  status: string
  created_at: string
}

export interface ApiKey {
  id: string
  name: string
  key_preview: string
  scopes: string[]
  expires_at: string | null
  usage_count: number
}

export interface OAuthClient {
  id: string
  name: string
  client_id: string
  redirect_uris: string[]
  allowed_scopes: string[]
  is_active: boolean
}

export interface DomainEvent {
  id: string
  event_type: string
  status: string
  created_at: string
}
