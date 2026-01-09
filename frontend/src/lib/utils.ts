import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date: Date | string): string {
  const dateObj = new Date(date);
  const now = new Date();
  const diffMs = now.getTime() - dateObj.getTime();
  const isFuture = diffMs < 0;
  const absDiffMs = Math.abs(diffMs);
  const diffSec = Math.floor(absDiffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHours = Math.floor(diffMin / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffSec < 10) {
    return "just now";
  }

  if (isFuture) {
    if (diffSec < 60) {
      return `in ${diffSec} seconds`;
    }
    if (diffMin < 60) {
      return `in ${diffMin} ${diffMin === 1 ? "minute" : "minutes"}`;
    }
    if (diffHours < 24) {
      return `in ${diffHours} ${diffHours === 1 ? "hour" : "hours"}`;
    }
    if (diffDays < 7) {
      return `in ${diffDays} ${diffDays === 1 ? "day" : "days"}`;
    }
  } else {
    if (diffSec < 60) {
      return `${diffSec} seconds ago`;
    }
    if (diffMin < 60) {
      return `${diffMin} ${diffMin === 1 ? "minute" : "minutes"} ago`;
    }
    if (diffHours < 24) {
      return `${diffHours} ${diffHours === 1 ? "hour" : "hours"} ago`;
    }
    if (diffDays < 7) {
      return `${diffDays} ${diffDays === 1 ? "day" : "days"} ago`;
    }
  }

  return dateObj.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function formatNumber(num: number): string {
  if (num >= 1000000) {
    const value = num / 1000000;
    return value % 1 === 0 ? `${Math.floor(value)}M` : `${value.toFixed(1)}M`;
  }
  if (num >= 1000) {
    const value = num / 1000;
    return value % 1 === 0 ? `${Math.floor(value)}K` : `${value.toFixed(1)}K`;
  }
  return num.toString();
}

export function copyToClipboard(text: string): Promise<void> {
  return navigator.clipboard.writeText(text);
}

export function isValidUrl(url: string): boolean {
  if (!url) return false;
  try {
    const urlObj = new URL(url);
    return urlObj.protocol === "http:" || urlObj.protocol === "https:";
  } catch {
    return false;
  }
}
