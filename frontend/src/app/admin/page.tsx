"use client";

import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Spinner } from "@/components/ui/spinner";
import { adminApi, authApi } from "@/lib/api";
import { formatNumber, copyToClipboard } from "@/lib/utils";
import {
  Shield,
  Users,
  Link2,
  MousePointer,
  TrendingUp,
  Calendar,
  Search,
  Trash2,
  Copy,
  Check,
  ExternalLink,
  AlertCircle,
  BarChart3,
} from "lucide-react";

interface AdminStats {
  total_urls: number;
  total_clicks: number;
  total_users: number;
  urls_today: number;
  clicks_today: number;
  urls_this_week: number;
  clicks_this_week: number;
}

interface TopUrl {
  id: string;
  short_code: string;
  original_url: string;
  clicks: number;
  user_email: string;
}

export default function AdminDashboard() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [topUrls, setTopUrls] = useState<TopUrl[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [isAdmin, setIsAdmin] = useState<boolean | null>(null);
  const router = useRouter();

  const checkAdminAndFetch = useCallback(async (token: string) => {
    try {
      const user = await authApi.me(token);
      if (!user.is_admin) {
        setIsAdmin(false);
        setIsLoading(false);
        return;
      }
      setIsAdmin(true);
      await Promise.all([fetchStats(token), fetchTopUrls(token)]);
    } catch {
      router.push("/login");
    }
  }, [router]);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.push("/login");
      return;
    }
    checkAdminAndFetch(token);
  }, [router, checkAdminAndFetch]);

  const fetchStats = async (token: string) => {
    try {
      const data = await adminApi.stats(token);
      setStats(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load stats");
    }
  };

  const fetchTopUrls = async (token: string) => {
    try {
      const data = await adminApi.topUrls(token, 20);
      setTopUrls(data.urls);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load top URLs");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = async (shortCode: string, id: string) => {
    const shortUrl = `${window.location.origin}/${shortCode}`;
    await copyToClipboard(shortUrl);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleDelete = async (shortCode: string, id: string) => {
    const token = localStorage.getItem("access_token");
    if (!token) return;

    if (!confirm("Are you sure you want to delete this URL? This action cannot be undone.")) {
      return;
    }

    setDeletingId(id);
    try {
      await adminApi.deleteUrl(shortCode, token);
      setTopUrls(topUrls.filter((u) => u.id !== id));
      // Refresh stats
      await fetchStats(token);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete URL");
    } finally {
      setDeletingId(null);
    }
  };

  const filteredUrls = topUrls.filter(
    (url) =>
      url.original_url.toLowerCase().includes(searchQuery.toLowerCase()) ||
      url.short_code.toLowerCase().includes(searchQuery.toLowerCase()) ||
      url.user_email.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (isLoading) {
    return (
      <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  if (isAdmin === false) {
    return (
      <div className="min-h-[calc(100vh-4rem)] py-8 px-4">
        <div className="max-w-2xl mx-auto">
          <Card>
            <CardContent className="pt-6">
              <div className="flex flex-col items-center text-center py-8">
                <Shield className="w-16 h-16 text-destructive mb-4" />
                <h2 className="text-2xl font-bold mb-2">Access Denied</h2>
                <p className="text-muted-foreground mb-6">
                  You do not have permission to access the admin dashboard.
                </p>
                <Button onClick={() => router.push("/dashboard")}>
                  Go to Dashboard
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-[calc(100vh-4rem)] py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-4 mb-8"
        >
          <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
            <Shield className="w-6 h-6 text-primary" />
          </div>
          <div>
            <h1 className="text-3xl font-bold">Admin Dashboard</h1>
            <p className="text-muted-foreground">
              EclipseInsight platform overview and content management
            </p>
          </div>
        </motion.div>

        {error && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            className="flex items-center gap-2 p-3 text-sm text-destructive bg-destructive/10 rounded-lg mb-6"
          >
            <AlertCircle className="w-4 h-4" />
            <span>{error}</span>
          </motion.div>
        )}

        {/* Stats Overview */}
        {stats && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8"
          >
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Total Users</p>
                    <p className="text-2xl font-bold">{formatNumber(stats.total_users)}</p>
                  </div>
                  <div className="w-10 h-10 rounded-full bg-blue-500/10 flex items-center justify-center">
                    <Users className="w-5 h-5 text-blue-500" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Total Links</p>
                    <p className="text-2xl font-bold">{formatNumber(stats.total_urls)}</p>
                  </div>
                  <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                    <Link2 className="w-5 h-5 text-primary" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Total Clicks</p>
                    <p className="text-2xl font-bold">{formatNumber(stats.total_clicks)}</p>
                  </div>
                  <div className="w-10 h-10 rounded-full bg-green-500/10 flex items-center justify-center">
                    <MousePointer className="w-5 h-5 text-green-500" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Clicks Today</p>
                    <p className="text-2xl font-bold">{formatNumber(stats.clicks_today)}</p>
                  </div>
                  <div className="w-10 h-10 rounded-full bg-yellow-500/10 flex items-center justify-center">
                    <TrendingUp className="w-5 h-5 text-yellow-500" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Activity Stats */}
        {stats && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8"
          >
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <Calendar className="w-5 h-5" />
                  Today&apos;s Activity
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-muted-foreground">New Links</span>
                    <span className="font-semibold">{formatNumber(stats.urls_today)}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-muted-foreground">Clicks</span>
                    <span className="font-semibold">{formatNumber(stats.clicks_today)}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <BarChart3 className="w-5 h-5" />
                  This Week
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-muted-foreground">New Links</span>
                    <span className="font-semibold">{formatNumber(stats.urls_this_week)}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-muted-foreground">Clicks</span>
                    <span className="font-semibold">{formatNumber(stats.clicks_this_week)}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Top URLs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card>
            <CardHeader>
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                  <CardTitle>Top Performing URLs</CardTitle>
                  <CardDescription>
                    {filteredUrls.length} of {topUrls.length} URLs
                  </CardDescription>
                </div>
                <div className="relative w-full sm:w-72">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <Input
                    placeholder="Search URLs or users..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {filteredUrls.length === 0 ? (
                <div className="text-center py-12">
                  <Link2 className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
                  <h3 className="text-lg font-medium">No URLs found</h3>
                  <p className="text-muted-foreground mt-1">
                    {searchQuery
                      ? "No URLs match your search"
                      : "No URLs have been created yet"}
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  <AnimatePresence>
                    {filteredUrls.map((url, index) => (
                      <motion.div
                        key={url.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: 20 }}
                        transition={{ delay: index * 0.03 }}
                        className="p-4 rounded-lg border bg-card hover:border-primary/50 transition-colors"
                      >
                        <div className="flex flex-col lg:flex-row gap-4">
                          {/* Rank */}
                          <div className="hidden lg:flex w-8 h-8 rounded-full bg-secondary items-center justify-center flex-shrink-0 text-sm font-medium">
                            {index + 1}
                          </div>

                          <div className="flex-1 min-w-0">
                            {/* Short Code & URL */}
                            <div className="flex items-center gap-2 mb-1">
                              <span className="font-mono text-primary font-medium">
                                /{url.short_code}
                              </span>
                              <span className="px-2 py-0.5 text-xs rounded-full bg-green-500/10 text-green-500">
                                {formatNumber(url.clicks)} clicks
                              </span>
                            </div>

                            {/* Original URL */}
                            <p className="text-sm text-muted-foreground truncate mb-1">
                              {url.original_url}
                            </p>

                            {/* User */}
                            <p className="text-xs text-muted-foreground">
                              Created by: {url.user_email}
                            </p>
                          </div>

                          {/* Actions */}
                          <div className="flex items-center gap-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleCopy(url.short_code, url.id)}
                            >
                              {copiedId === url.id ? (
                                <Check className="w-4 h-4" />
                              ) : (
                                <Copy className="w-4 h-4" />
                              )}
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() =>
                                window.open(`${window.location.origin}/${url.short_code}`, "_blank")
                              }
                            >
                              <ExternalLink className="w-4 h-4" />
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleDelete(url.short_code, url.id)}
                              disabled={deletingId === url.id}
                              className="text-destructive hover:text-destructive"
                            >
                              {deletingId === url.id ? (
                                <Spinner size="sm" />
                              ) : (
                                <Trash2 className="w-4 h-4" />
                              )}
                            </Button>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </AnimatePresence>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
