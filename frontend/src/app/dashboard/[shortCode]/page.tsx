"use client";

import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import { urlApi } from "@/lib/api";
import { formatNumber, copyToClipboard } from "@/lib/utils";
import {
  ArrowLeft,
  Copy,
  Check,
  ExternalLink,
  BarChart3,
  Globe,
  Monitor,
  TrendingUp,
  Link2,
  Calendar,
  MousePointer,
  AlertCircle,
} from "lucide-react";

interface UrlStats {
  short_code: string;
  original_url: string;
  total_clicks: number;
  clicks_today: number;
  clicks_this_week: number;
  top_referrers: Array<{ referrer: string; count: number }>;
  clicks_by_country: Array<{ country: string; count: number }>;
  clicks_by_device: Array<{ device: string; count: number }>;
  clicks_over_time: Array<{ date: string; count: number }>;
}

// Simple bar chart component
function SimpleBarChart({
  data,
  maxValue
}: {
  data: Array<{ label: string; value: number }>;
  maxValue: number;
}) {
  return (
    <div className="space-y-3">
      {data.map((item, index) => (
        <motion.div
          key={item.label}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: index * 0.1 }}
          className="space-y-1"
        >
          <div className="flex justify-between text-sm">
            <span className="truncate flex-1 mr-2">{item.label}</span>
            <span className="text-muted-foreground">{formatNumber(item.value)}</span>
          </div>
          <div className="h-2 bg-secondary rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${maxValue > 0 ? (item.value / maxValue) * 100 : 0}%` }}
              transition={{ delay: index * 0.1 + 0.2, duration: 0.5 }}
              className="h-full bg-primary rounded-full"
            />
          </div>
        </motion.div>
      ))}
    </div>
  );
}

// Time series chart component
function TimeSeriesChart({ data }: { data: Array<{ date: string; count: number }> }) {
  const maxValue = Math.max(...data.map(d => d.count), 1);
  const chartHeight = 120;

  return (
    <div className="flex items-end gap-1 h-32">
      {data.map((item, index) => (
        <motion.div
          key={item.date}
          initial={{ height: 0 }}
          animate={{ height: `${(item.count / maxValue) * chartHeight}px` }}
          transition={{ delay: index * 0.05, duration: 0.3 }}
          className="flex-1 bg-primary/80 hover:bg-primary rounded-t transition-colors min-h-[4px] relative group"
        >
          <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-popover px-2 py-1 rounded text-xs opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap border shadow-sm z-10">
            {item.count} clicks
            <div className="text-muted-foreground">{item.date}</div>
          </div>
        </motion.div>
      ))}
    </div>
  );
}

export default function UrlStatsPage() {
  const [stats, setStats] = useState<UrlStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const router = useRouter();
  const params = useParams();
  const shortCode = params.shortCode as string;

  const fetchStats = useCallback(async (token: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await urlApi.stats(shortCode, token);
      setStats(data);
    } catch (err) {
      console.error("Stats fetch error:", err);
      setError(err instanceof Error ? err.message : "Failed to load stats");
    } finally {
      setIsLoading(false);
    }
  }, [shortCode]);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.push("/login");
      return;
    }
    fetchStats(token);
  }, [router, fetchStats]);

  const handleCopy = async () => {
    if (stats) {
      const shortUrl = `${window.location.origin}/${stats.short_code}`;
      await copyToClipboard(shortUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const baseUrl = typeof window !== "undefined" ? window.location.origin : "";
  const shortUrl = stats ? `${baseUrl}/${stats.short_code}` : "";

  if (isLoading) {
    return (
      <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-[calc(100vh-4rem)] py-8 px-4">
        <div className="max-w-4xl mx-auto">
          <Card>
            <CardContent className="pt-6">
              <div className="flex flex-col items-center text-center py-8">
                <AlertCircle className="w-12 h-12 text-destructive mb-4" />
                <h2 className="text-xl font-semibold mb-2">Error Loading Stats</h2>
                <p className="text-muted-foreground mb-4">{error}</p>
                <Link href="/dashboard">
                  <Button>
                    <ArrowLeft className="w-4 h-4 mr-2" />
                    Back to Dashboard
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  if (!stats) {
    return null;
  }

  const deviceData = stats.clicks_by_device.map(d => ({ label: d.device, value: d.count }));
  const countryData = stats.clicks_by_country.map(c => ({ label: c.country, value: c.count }));
  const referrerData = stats.top_referrers.map(r => ({
    label: r.referrer || "Direct",
    value: r.count
  }));

  const maxDeviceValue = Math.max(...deviceData.map(d => d.value), 1);
  const maxCountryValue = Math.max(...countryData.map(c => c.value), 1);
  const maxReferrerValue = Math.max(...referrerData.map(r => r.value), 1);

  return (
    <div className="min-h-[calc(100vh-4rem)] py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <Link href="/dashboard">
            <Button variant="ghost" size="sm" className="mb-4">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Dashboard
            </Button>
          </Link>

          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                  <Link2 className="w-5 h-5 text-primary" />
                </div>
                <h1 className="text-2xl font-bold truncate">{shortUrl}</h1>
              </div>
              <p className="text-muted-foreground truncate">{stats.original_url}</p>
            </div>

            <div className="flex items-center gap-2">
              <Button variant="outline" onClick={handleCopy}>
                {copied ? (
                  <Check className="w-4 h-4 mr-2" />
                ) : (
                  <Copy className="w-4 h-4 mr-2" />
                )}
                {copied ? "Copied!" : "Copy"}
              </Button>
              <Button
                variant="outline"
                onClick={() => window.open(shortUrl, "_blank")}
              >
                <ExternalLink className="w-4 h-4 mr-2" />
                Visit
              </Button>
            </div>
          </div>
        </motion.div>

        {/* Stats Overview */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8"
        >
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Total Clicks</p>
                  <p className="text-3xl font-bold">{formatNumber(stats.total_clicks)}</p>
                </div>
                <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
                  <MousePointer className="w-6 h-6 text-primary" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Today</p>
                  <p className="text-3xl font-bold">{formatNumber(stats.clicks_today)}</p>
                </div>
                <div className="w-12 h-12 rounded-full bg-green-500/10 flex items-center justify-center">
                  <Calendar className="w-6 h-6 text-green-500" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">This Week</p>
                  <p className="text-3xl font-bold">{formatNumber(stats.clicks_this_week)}</p>
                </div>
                <div className="w-12 h-12 rounded-full bg-blue-500/10 flex items-center justify-center">
                  <TrendingUp className="w-6 h-6 text-blue-500" />
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Clicks Over Time */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card className="h-full">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="w-5 h-5" />
                  Clicks Over Time
                </CardTitle>
                <CardDescription>Last 7 days performance</CardDescription>
              </CardHeader>
              <CardContent>
                {stats.clicks_over_time.length > 0 ? (
                  <TimeSeriesChart data={stats.clicks_over_time} />
                ) : (
                  <div className="flex items-center justify-center h-32 text-muted-foreground">
                    No click data yet
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>

          {/* Top Referrers */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card className="h-full">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <ExternalLink className="w-5 h-5" />
                  Top Referrers
                </CardTitle>
                <CardDescription>Where your clicks come from</CardDescription>
              </CardHeader>
              <CardContent>
                {referrerData.length > 0 ? (
                  <SimpleBarChart data={referrerData.slice(0, 5)} maxValue={maxReferrerValue} />
                ) : (
                  <div className="flex items-center justify-center h-32 text-muted-foreground">
                    No referrer data yet
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Second Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Devices */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <Card className="h-full">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Monitor className="w-5 h-5" />
                  Devices
                </CardTitle>
                <CardDescription>Breakdown by device type</CardDescription>
              </CardHeader>
              <CardContent>
                {deviceData.length > 0 ? (
                  <SimpleBarChart data={deviceData.slice(0, 5)} maxValue={maxDeviceValue} />
                ) : (
                  <div className="flex items-center justify-center h-32 text-muted-foreground">
                    No device data yet
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>

          {/* Countries */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <Card className="h-full">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Globe className="w-5 h-5" />
                  Countries
                </CardTitle>
                <CardDescription>Geographic distribution</CardDescription>
              </CardHeader>
              <CardContent>
                {countryData.length > 0 ? (
                  <SimpleBarChart data={countryData.slice(0, 5)} maxValue={maxCountryValue} />
                ) : (
                  <div className="flex items-center justify-center h-32 text-muted-foreground">
                    No geographic data yet
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
