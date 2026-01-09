"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Spinner } from "@/components/ui/spinner";
import { urlApi } from "@/lib/api";
import { formatDate, formatNumber, copyToClipboard } from "@/lib/utils";
import {
  Link2,
  Copy,
  Check,
  Trash2,
  BarChart3,
  ExternalLink,
  Plus,
  Search,
  AlertCircle,
  Brain,
  Tag,
} from "lucide-react";
import type { ShortURL } from "@/types";

export default function DashboardPage() {
  const [urls, setUrls] = useState<ShortURL[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.push("/login");
      return;
    }
    fetchUrls(token);
  }, [router]);

  const fetchUrls = async (token: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await urlApi.list(token);
      setUrls(data.map(u => ({
        id: u.id,
        original_url: u.original_url,
        short_code: u.short_code,
        short_url: u.short_url,
        clicks: u.clicks,
        created_at: u.created_at,
        expiration: u.expiration,
        preview_title: u.preview_title,
        preview_description: u.preview_description,
        preview_image: u.preview_image,
        ai: u.ai ? {
          tags: u.ai.tags,
          summary: u.ai.summary,
          suggested_alias: u.ai.suggested_alias,
          is_toxic: u.ai.is_toxic,
          analyzed: u.ai.analyzed,
          analyzed_at: u.ai.analyzed_at,
          error: u.ai.error,
        } : null,
      })));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load URLs");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = async (shortUrl: string, id: string) => {
    await copyToClipboard(shortUrl);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleDelete = async (shortCode: string, id: string) => {
    const token = localStorage.getItem("access_token");
    if (!token) return;

    setDeletingId(id);
    try {
      await urlApi.delete(shortCode, token);
      setUrls(urls.filter((u) => u.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete URL");
    } finally {
      setDeletingId(null);
    }
  };

  const filteredUrls = urls.filter(
    (url) =>
      url.original_url.toLowerCase().includes(searchQuery.toLowerCase()) ||
      url.short_code.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (url.ai?.tags?.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase())))
  );

  const totalClicks = urls.reduce((sum, url) => sum + url.clicks, 0);
  const aiAnalyzedCount = urls.filter(url => url.ai?.analyzed).length;

  return (
    <div className="min-h-[calc(100vh-4rem)] py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8"
        >
          <div>
            <h1 className="text-3xl font-bold">Dashboard</h1>
            <p className="text-muted-foreground mt-1">
              Manage and track your shortened URLs
            </p>
          </div>
          <Link href="/shorten">
            <Button variant="gradient">
              <Plus className="w-4 h-4 mr-2" />
              New Short Link
            </Button>
          </Link>
        </motion.div>

        {/* Stats Cards */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8"
        >
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Total Links</p>
                  <p className="text-3xl font-bold">{formatNumber(urls.length)}</p>
                </div>
                <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
                  <Link2 className="w-6 h-6 text-primary" />
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Total Clicks</p>
                  <p className="text-3xl font-bold">{formatNumber(totalClicks)}</p>
                </div>
                <div className="w-12 h-12 rounded-full bg-green-500/10 flex items-center justify-center">
                  <BarChart3 className="w-6 h-6 text-green-500" />
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Avg. Clicks/Link</p>
                  <p className="text-3xl font-bold">
                    {urls.length > 0 ? formatNumber(Math.round(totalClicks / urls.length)) : "0"}
                  </p>
                </div>
                <div className="w-12 h-12 rounded-full bg-blue-500/10 flex items-center justify-center">
                  <BarChart3 className="w-6 h-6 text-blue-500" />
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">AI Analyzed</p>
                  <p className="text-3xl font-bold">{formatNumber(aiAnalyzedCount)}</p>
                </div>
                <div className="w-12 h-12 rounded-full bg-purple-500/10 flex items-center justify-center">
                  <Brain className="w-6 h-6 text-purple-500" />
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Search and URLs List */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card>
            <CardHeader>
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                  <CardTitle>Your Links</CardTitle>
                  <CardDescription>
                    {filteredUrls.length} of {urls.length} links
                  </CardDescription>
                </div>
                <div className="relative w-full sm:w-64">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <Input
                    placeholder="Search links..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {error && (
                <div className="flex items-center gap-2 p-3 text-sm text-destructive bg-destructive/10 rounded-lg mb-4">
                  <AlertCircle className="w-4 h-4" />
                  <span>{error}</span>
                </div>
              )}

              {isLoading ? (
                <div className="flex items-center justify-center py-12">
                  <Spinner size="lg" />
                </div>
              ) : filteredUrls.length === 0 ? (
                <div className="text-center py-12">
                  <Link2 className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
                  <h3 className="text-lg font-medium">No links yet</h3>
                  <p className="text-muted-foreground mt-1 mb-4">
                    {searchQuery ? "No links match your search" : "Create your first short link to get started"}
                  </p>
                  {!searchQuery && (
                    <Link href="/shorten">
                      <Button variant="gradient">
                        <Plus className="w-4 h-4 mr-2" />
                        Create Short Link
                      </Button>
                    </Link>
                  )}
                </div>
              ) : (
                <div className="space-y-4">
                  <AnimatePresence>
                    {filteredUrls.map((url, index) => (
                      <motion.div
                        key={url.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: 20 }}
                        transition={{ delay: index * 0.05 }}
                        className="p-4 rounded-lg border bg-card hover:border-primary/50 transition-colors"
                      >
                        <div className="flex flex-col sm:flex-row gap-4">
                          {/* URL Icon placeholder - PNG: 32x32, glowing blue link symbol */}
                          <div className="hidden sm:flex w-10 h-10 rounded-lg bg-primary/10 items-center justify-center flex-shrink-0">
                            <Link2 className="w-5 h-5 text-primary" />
                          </div>

                          <div className="flex-1 min-w-0">
                            {/* Short URL */}
                            <div className="flex items-center gap-2 mb-1">
                              <a
                                href={url.short_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="font-medium text-primary hover:underline truncate"
                              >
                                {url.short_url}
                              </a>
                              <button
                                onClick={() => handleCopy(url.short_url, url.id)}
                                className="p-1 hover:bg-secondary rounded"
                                aria-label="Copy"
                              >
                                {copiedId === url.id ? (
                                  <Check className="w-4 h-4 text-green-500" />
                                ) : (
                                  <Copy className="w-4 h-4 text-muted-foreground" />
                                )}
                              </button>
                            </div>

                            {/* Original URL */}
                            <p className="text-sm text-muted-foreground truncate">
                              {url.original_url}
                            </p>

                            {/* Stats */}
                            <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                              <span className="flex items-center gap-1">
                                <BarChart3 className="w-3 h-3" />
                                {formatNumber(url.clicks)} clicks
                              </span>
                              <span>Created {formatDate(url.created_at)}</span>
                              {url.expiration && (
                                <span className="text-yellow-500">
                                  Expires {formatDate(url.expiration)}
                                </span>
                              )}
                            </div>

                            {/* AI Tags */}
                            {url.ai?.analyzed && url.ai.tags && url.ai.tags.length > 0 && (
                              <div className="flex flex-wrap items-center gap-1.5 mt-2">
                                <Brain className="w-3 h-3 text-primary" />
                                {url.ai.tags.slice(0, 4).map((tag) => (
                                  <span
                                    key={tag}
                                    className="px-1.5 py-0.5 text-xs rounded-full bg-primary/10 text-primary border border-primary/20"
                                  >
                                    {tag}
                                  </span>
                                ))}
                                {url.ai.tags.length > 4 && (
                                  <span className="text-xs text-muted-foreground">
                                    +{url.ai.tags.length - 4} more
                                  </span>
                                )}
                              </div>
                            )}

                            {/* AI Summary */}
                            {url.ai?.analyzed && url.ai.summary && (
                              <p className="text-xs text-muted-foreground mt-1 line-clamp-1">
                                {url.ai.summary}
                              </p>
                            )}
                          </div>

                          {/* Actions */}
                          <div className="flex items-center gap-2">
                            <Link href={`/dashboard/${url.short_code}`}>
                              <Button variant="outline" size="sm">
                                <BarChart3 className="w-4 h-4 mr-1" />
                                Stats
                              </Button>
                            </Link>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => window.open(url.short_url, "_blank")}
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
