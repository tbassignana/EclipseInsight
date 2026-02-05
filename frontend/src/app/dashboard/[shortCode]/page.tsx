"use client";

import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import { urlApi, type URLResponse } from "@/lib/api";
import { formatNumber, copyToClipboard, formatDate } from "@/lib/utils";
import {
  ArrowLeft,
  Copy,
  Check,
  ExternalLink,
  BarChart3,
  Globe,
  Monitor,
  TrendingUp,
  Calendar,
  MousePointer,
  AlertCircle,
  Brain,
  Tags,
  FileText,
  Wand2,
  ShieldCheck,
  ShieldAlert,
  Image as ImageIcon,
  Clock,
  QrCode,
  Download,
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

type DatePreset = "7d" | "30d" | "90d" | "all";

export default function UrlStatsPage() {
  const [stats, setStats] = useState<UrlStats | null>(null);
  const [urlDetails, setUrlDetails] = useState<URLResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [datePreset, setDatePreset] = useState<DatePreset>("all");
  const [customDateFrom, setCustomDateFrom] = useState("");
  const [customDateTo, setCustomDateTo] = useState("");
  const [isExporting, setIsExporting] = useState(false);
  const router = useRouter();
  const params = useParams();
  const shortCode = params.shortCode as string;

  const getDateRange = useCallback((): { dateFrom?: string; dateTo?: string } => {
    // Custom date inputs override presets
    if (customDateFrom || customDateTo) {
      const result: { dateFrom?: string; dateTo?: string } = {};
      if (customDateFrom) result.dateFrom = new Date(customDateFrom).toISOString();
      if (customDateTo) result.dateTo = new Date(customDateTo + "T23:59:59").toISOString();
      return result;
    }
    if (datePreset === "all") return {};
    const days = datePreset === "7d" ? 7 : datePreset === "30d" ? 30 : 90;
    const from = new Date();
    from.setDate(from.getDate() - days);
    return { dateFrom: from.toISOString() };
  }, [datePreset, customDateFrom, customDateTo]);

  const fetchData = useCallback(async (token: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const { dateFrom, dateTo } = getDateRange();
      const [statsData, urlData] = await Promise.all([
        urlApi.stats(shortCode, token, dateFrom, dateTo),
        urlApi.get(shortCode, token),
      ]);
      setStats(statsData);
      setUrlDetails(urlData);
    } catch (err) {
      console.error("Data fetch error:", err);
      setError(err instanceof Error ? err.message : "Failed to load data");
    } finally {
      setIsLoading(false);
    }
  }, [shortCode, getDateRange]);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.push("/login");
      return;
    }
    fetchData(token);
  }, [router, fetchData]);

  const handleExportCsv = async () => {
    const token = localStorage.getItem("access_token");
    if (!token) return;
    setIsExporting(true);
    try {
      const { dateFrom, dateTo } = getDateRange();
      const blob = await urlApi.exportStatsCsv(shortCode, token, dateFrom, dateTo);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${shortCode}-analytics.csv`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Export failed");
    } finally {
      setIsExporting(false);
    }
  };

  const handleCopy = async () => {
    if (urlDetails) {
      await copyToClipboard(urlDetails.short_url);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  // Use the short_url from API which has the correct backend BASE_URL
  const shortUrl = urlDetails?.short_url || "";

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
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-red-600 to-red-900 flex items-center justify-center flex-shrink-0 shadow-lg shadow-red-500/20">
                  <Brain className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold truncate">{shortUrl}</h1>
                  <div className="flex items-center gap-2 text-sm">
                    {urlDetails?.ai?.analyzed && (
                      <span className="flex items-center gap-1 text-primary">
                        <Brain className="w-3 h-3" />
                        AI Analyzed
                      </span>
                    )}
                    {urlDetails?.ai?.is_toxic === false && (
                      <span className="flex items-center gap-1 text-green-500">
                        <ShieldCheck className="w-3 h-3" />
                        Safe
                      </span>
                    )}
                    {urlDetails?.expiration && (
                      <span className="flex items-center gap-1 text-muted-foreground">
                        <Clock className="w-3 h-3" />
                        Expires {formatDate(urlDetails.expiration)}
                      </span>
                    )}
                  </div>
                </div>
              </div>
              <p className="text-muted-foreground truncate ml-13">{stats.original_url}</p>
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
              <Button
                variant="outline"
                onClick={handleExportCsv}
                disabled={isExporting}
              >
                <Download className="w-4 h-4 mr-2" />
                {isExporting ? "Exporting..." : "CSV"}
              </Button>
            </div>
          </div>
        </motion.div>

        {/* Date Range Filter */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.05 }}
          className="mb-6"
        >
          <Card>
            <CardContent className="pt-6">
              <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
                <span className="text-sm font-medium text-muted-foreground flex items-center gap-1.5">
                  <Calendar className="w-4 h-4" />
                  Date Range:
                </span>
                <div className="flex flex-wrap gap-2">
                  {(["7d", "30d", "90d", "all"] as DatePreset[]).map((preset) => (
                    <Button
                      key={preset}
                      variant={datePreset === preset ? "default" : "outline"}
                      size="sm"
                      onClick={() => {
                        setDatePreset(preset);
                        setCustomDateFrom("");
                        setCustomDateTo("");
                      }}
                    >
                      {preset === "all" ? "All Time" : preset === "7d" ? "7 Days" : preset === "30d" ? "30 Days" : "90 Days"}
                    </Button>
                  ))}
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type="date"
                    value={customDateFrom}
                    onChange={(e) => setCustomDateFrom(e.target.value)}
                    className="h-9 px-3 rounded-md border border-input bg-background text-sm"
                    placeholder="From"
                  />
                  <span className="text-muted-foreground text-sm">to</span>
                  <input
                    type="date"
                    value={customDateTo}
                    onChange={(e) => setCustomDateTo(e.target.value)}
                    className="h-9 px-3 rounded-md border border-input bg-background text-sm"
                    placeholder="To"
                  />
                </div>
              </div>
            </CardContent>
          </Card>
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

        {/* AI Insights & Preview Section */}
        {urlDetails && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
            className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8"
          >
            {/* AI Analysis Card */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Brain className="w-5 h-5 text-primary" />
                  AI Content Analysis
                </CardTitle>
                <CardDescription>
                  {urlDetails.ai?.analyzed
                    ? `Analyzed ${urlDetails.ai.analyzed_at ? formatDate(urlDetails.ai.analyzed_at) : "recently"}`
                    : "Content analysis powered by Claude AI"}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {urlDetails.ai?.analyzed ? (
                  <>
                    {/* Summary */}
                    {urlDetails.ai.summary && (
                      <div className="space-y-2">
                        <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                          <FileText className="w-4 h-4" />
                          AI Summary
                        </div>
                        <p className="text-sm bg-secondary/50 p-3 rounded-lg">
                          {urlDetails.ai.summary}
                        </p>
                      </div>
                    )}

                    {/* Tags */}
                    {urlDetails.ai.tags && urlDetails.ai.tags.length > 0 && (
                      <div className="space-y-2">
                        <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                          <Tags className="w-4 h-4" />
                          Auto-Generated Tags
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {urlDetails.ai.tags.map((tag, index) => (
                            <motion.span
                              key={tag}
                              initial={{ opacity: 0, scale: 0.8 }}
                              animate={{ opacity: 1, scale: 1 }}
                              transition={{ delay: index * 0.05 }}
                              className="px-3 py-1 text-sm font-medium rounded-full bg-primary/10 text-primary border border-primary/20"
                            >
                              {tag}
                            </motion.span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Suggested Alias & Safety Status */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      {urlDetails.ai.suggested_alias && (
                        <div className="space-y-2">
                          <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                            <Wand2 className="w-4 h-4" />
                            Suggested Alias
                          </div>
                          <p className="font-mono text-sm text-primary bg-primary/5 p-2 rounded border border-primary/10">
                            /{urlDetails.ai.suggested_alias}
                          </p>
                        </div>
                      )}
                      <div className="space-y-2">
                        <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                          {urlDetails.ai.is_toxic ? (
                            <ShieldAlert className="w-4 h-4 text-destructive" />
                          ) : (
                            <ShieldCheck className="w-4 h-4 text-green-500" />
                          )}
                          Content Safety
                        </div>
                        <div className={`flex items-center gap-2 p-2 rounded border ${
                          urlDetails.ai.is_toxic
                            ? "bg-destructive/10 border-destructive/20 text-destructive"
                            : "bg-green-500/10 border-green-500/20 text-green-600 dark:text-green-400"
                        }`}>
                          {urlDetails.ai.is_toxic ? (
                            <>
                              <ShieldAlert className="w-4 h-4" />
                              <span className="text-sm font-medium">Flagged as potentially harmful</span>
                            </>
                          ) : (
                            <>
                              <ShieldCheck className="w-4 h-4" />
                              <span className="text-sm font-medium">Content verified safe</span>
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="flex flex-col items-center justify-center py-8 text-center">
                    <Brain className="w-12 h-12 text-muted-foreground mb-4" />
                    <p className="text-muted-foreground">
                      AI analysis was skipped for this link
                    </p>
                    <p className="text-sm text-muted-foreground mt-1">
                      Enable AI analysis when creating links to get insights
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Link Preview & QR Code Column */}
            <div className="space-y-6">
              {/* Link Preview Card */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <ImageIcon className="w-5 h-5" />
                    Link Preview
                  </CardTitle>
                  <CardDescription>
                    How this link appears when shared
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {urlDetails.preview_title || urlDetails.preview_description || urlDetails.preview_image ? (
                    <div className="space-y-3">
                      {urlDetails.preview_image && (
                        <div className="aspect-video rounded-lg bg-muted overflow-hidden">
                          <img
                            src={urlDetails.preview_image}
                            alt="Link preview"
                            className="w-full h-full object-cover"
                          />
                        </div>
                      )}
                      {urlDetails.preview_title && (
                        <h4 className="font-semibold text-sm line-clamp-2">
                          {urlDetails.preview_title}
                        </h4>
                      )}
                      {urlDetails.preview_description && (
                        <p className="text-sm text-muted-foreground line-clamp-3">
                          {urlDetails.preview_description}
                        </p>
                      )}
                    </div>
                  ) : (
                    <div className="flex flex-col items-center justify-center py-8 text-center">
                      <ImageIcon className="w-10 h-10 text-muted-foreground mb-3" />
                      <p className="text-sm text-muted-foreground">
                        No preview available
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* QR Code Card */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <QrCode className="w-5 h-5" />
                    QR Code
                  </CardTitle>
                  <CardDescription>
                    Scan to visit this link
                  </CardDescription>
                </CardHeader>
                <CardContent className="flex flex-col items-center gap-3">
                  <div className="bg-white p-4 rounded-lg">
                    <img
                      src={urlApi.qrCodeUrl(shortCode)}
                      alt={`QR code for ${shortCode}`}
                      className="w-40 h-40"
                    />
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      const a = document.createElement("a");
                      a.href = urlApi.qrCodeUrl(shortCode);
                      a.download = `${shortCode}-qr.png`;
                      a.click();
                    }}
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Download PNG
                  </Button>
                </CardContent>
              </Card>
            </div>
          </motion.div>
        )}

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
