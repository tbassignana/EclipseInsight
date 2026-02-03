const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface ApiOptions extends RequestInit {
  token?: string;
}

async function apiRequest<T>(
  endpoint: string,
  options: ApiOptions = {}
): Promise<T> {
  const { token, ...fetchOptions } = options;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...fetchOptions,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "An error occurred" }));
    throw new Error(error.detail || "An error occurred");
  }

  return response.json();
}

// AI Analysis types
export interface AIAnalysis {
  tags: string[];
  summary: string | null;
  suggested_alias: string | null;
  is_toxic: boolean;
  analyzed: boolean;
  analyzed_at: string | null;
  error?: string | null;
}

// URL Response type
export interface URLResponse {
  id: string;
  short_code: string;
  short_url: string;
  original_url: string;
  clicks: number;
  created_at: string;
  expiration?: string | null;
  preview_title?: string | null;
  preview_description?: string | null;
  preview_image?: string | null;
  ai?: AIAnalysis | null;
}

// Auth API
export const authApi = {
  register: (email: string, password: string) =>
    apiRequest<{ id: string; email: string }>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  login: (email: string, password: string) =>
    apiRequest<{ access_token: string; token_type: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  me: (token: string) =>
    apiRequest<{ id: string; email: string; is_admin: boolean }>("/auth/me", {
      token,
    }),

  forgotPassword: (email: string) =>
    apiRequest<{ message: string }>("/auth/forgot-password", {
      method: "POST",
      body: JSON.stringify({ email }),
    }),

  resetPassword: (token: string, newPassword: string) =>
    apiRequest<{ message: string }>("/auth/reset-password", {
      method: "POST",
      body: JSON.stringify({ token, new_password: newPassword }),
    }),
};

// URL API
export const urlApi = {
  shorten: (
    originalUrl: string,
    options: {
      customAlias?: string;
      expirationDays?: number;
      skipAiAnalysis?: boolean;
      useAiSuggestedAlias?: boolean;
    },
    token: string
  ) =>
    apiRequest<URLResponse>("/urls/shorten", {
      method: "POST",
      body: JSON.stringify({
        original_url: originalUrl,
        custom_alias: options.customAlias,
        expiration_days: options.expirationDays,
        skip_ai_analysis: options.skipAiAnalysis,
        use_ai_suggested_alias: options.useAiSuggestedAlias,
      }),
      token,
    }),

  list: (token: string) =>
    apiRequest<URLResponse[]>("/urls", { token }),

  get: (shortCode: string, token: string) =>
    apiRequest<URLResponse>(`/urls/${shortCode}`, { token }),

  stats: (shortCode: string, token: string) =>
    apiRequest<{
      short_code: string;
      original_url: string;
      total_clicks: number;
      clicks_today: number;
      clicks_this_week: number;
      top_referrers: Array<{ referrer: string; count: number }>;
      clicks_by_country: Array<{ country: string; count: number }>;
      clicks_by_device: Array<{ device: string; count: number }>;
      clicks_over_time: Array<{ date: string; count: number }>;
    }>(`/urls/${shortCode}/stats`, { token }),

  update: (
    shortCode: string,
    data: { original_url?: string; custom_alias?: string; expiration_days?: number },
    token: string
  ) =>
    apiRequest<URLResponse>(`/urls/${shortCode}`, {
      method: "PATCH",
      body: JSON.stringify(data),
      token,
    }),

  delete: (shortCode: string, token: string) =>
    apiRequest<{ message: string }>(`/urls/${shortCode}`, {
      method: "DELETE",
      token,
    }),

  preview: (url: string) =>
    apiRequest<{
      title?: string;
      description?: string;
      image?: string;
      url: string;
    }>(`/urls/preview?url=${encodeURIComponent(url)}`),
};

// Admin API
export const adminApi = {
  stats: (token: string) =>
    apiRequest<{
      total_urls: number;
      total_clicks: number;
      total_users: number;
      urls_today: number;
      clicks_today: number;
      urls_this_week: number;
      clicks_this_week: number;
    }>("/admin/stats/summary", { token }),

  topUrls: (token: string, limit: number = 10) =>
    apiRequest<{
      urls: Array<{
        id: string;
        short_code: string;
        original_url: string;
        clicks: number;
        user_email: string;
      }>;
      count: number;
    }>(`/admin/top-urls?limit=${limit}`, { token }),

  deleteUrl: (shortCode: string, token: string) =>
    apiRequest<{ message: string }>(`/admin/urls/${shortCode}`, {
      method: "DELETE",
      token,
    }),
};
