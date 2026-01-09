export interface User {
  id: string;
  email: string;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
}

export interface AIAnalysisData {
  tags: string[];
  summary: string | null;
  suggested_alias: string | null;
  is_toxic: boolean;
  analyzed: boolean;
  analyzed_at: string | null;
  error?: string | null;
}

export interface ShortURL {
  id: string;
  original_url: string;
  short_code: string;
  short_url: string;
  clicks: number;
  expiration?: string | null;
  created_at: string;
  preview_title?: string | null;
  preview_description?: string | null;
  preview_image?: string | null;
  ai?: AIAnalysisData | null;
}

export interface URLStats {
  short_code: string;
  original_url: string;
  total_clicks: number;
  clicks_today: number;
  clicks_this_week: number;
  top_referrers: ReferrerData[];
  clicks_by_country: CountryData[];
  clicks_by_device: DeviceData[];
  clicks_over_time: TimeSeriesData[];
}

export interface ReferrerData {
  referrer: string;
  count: number;
}

export interface CountryData {
  country: string;
  count: number;
}

export interface DeviceData {
  device: string;
  count: number;
}

export interface TimeSeriesData {
  date: string;
  count: number;
}

export interface URLPreview {
  title?: string;
  description?: string;
  image?: string;
  url: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  error: string | null;
}
