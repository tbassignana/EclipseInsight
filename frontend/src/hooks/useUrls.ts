"use client";

import useSWR, { mutate } from "swr";
import { urlApi, type URLResponse } from "@/lib/api";

// SWR fetcher that uses the token from localStorage
const fetchUrls = async (): Promise<URLResponse[]> => {
  const token = localStorage.getItem("access_token");
  if (!token) throw new Error("Not authenticated");
  return urlApi.list(token);
};

const fetchUrlStats = async (shortCode: string) => {
  const token = localStorage.getItem("access_token");
  if (!token) throw new Error("Not authenticated");
  return urlApi.stats(shortCode, token);
};

export function useUrls() {
  const { data, error, isLoading, isValidating } = useSWR<URLResponse[]>(
    "urls",
    fetchUrls,
    {
      revalidateOnFocus: true,
      revalidateOnReconnect: true,
      dedupingInterval: 5000, // Dedupe requests within 5 seconds
    }
  );

  const deleteUrl = async (shortCode: string) => {
    const token = localStorage.getItem("access_token");
    if (!token) throw new Error("Not authenticated");

    // Optimistic update
    const previousUrls = data;
    mutate(
      "urls",
      data?.filter((u) => u.short_code !== shortCode),
      false
    );

    try {
      await urlApi.delete(shortCode, token);
      // Revalidate after successful delete
      mutate("urls");
    } catch (err) {
      // Rollback on error
      mutate("urls", previousUrls, false);
      throw err;
    }
  };

  const refreshUrls = () => mutate("urls");

  return {
    urls: data || [],
    isLoading,
    isRefreshing: isValidating,
    error,
    deleteUrl,
    refreshUrls,
  };
}

export function useUrlStats(shortCode: string | null) {
  const { data, error, isLoading } = useSWR(
    shortCode ? `url-stats-${shortCode}` : null,
    () => (shortCode ? fetchUrlStats(shortCode) : null),
    {
      revalidateOnFocus: true,
      refreshInterval: 30000, // Refresh stats every 30 seconds
    }
  );

  return {
    stats: data,
    isLoading,
    error,
  };
}
