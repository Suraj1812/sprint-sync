export interface ApiError {
  code: string
  message: string
}

export type ApiResponse<T = unknown> =
  | { success: true; data: T }
  | { success: false; error: ApiError }

export type Theme = "light" | "dark" | "system"
