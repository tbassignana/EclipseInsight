"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import { urlApi, type AIAnalysis } from "@/lib/api";
import { copyToClipboard, isValidUrl } from "@/lib/utils";
import {
  Link2,
  Copy,
  Check,
  AlertCircle,
  Sparkles,
  Calendar,
  ExternalLink,
  Image as ImageIcon,
  Brain,
  Tag,
  FileText,
  Wand2,
  QrCode,
  Download,
  AlertTriangle,
} from "lucide-react";

interface URLPreview {
  title?: string;
  description?: string;
  image?: string;
}

interface ShortenResult {
  shortUrl: string;
  shortCode: string;
  ai?: AIAnalysis | null;
}

export default function ShortenPage() {
  const [url, setUrl] = useState("");
  const [customAlias, setCustomAlias] = useState("");
  const [expirationDays, setExpirationDays] = useState<number | "">("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ShortenResult | null>(null);
  const [copied, setCopied] = useState(false);
  const [preview, setPreview] = useState<URLPreview | null>(null);
  const [isLoadingPreview, setIsLoadingPreview] = useState(false);
  const [skipAiAnalysis, setSkipAiAnalysis] = useState(false);
  const [useAiSuggestedAlias, setUseAiSuggestedAlias] = useState(false);
  const [urlCount, setUrlCount] = useState(0);
  const MAX_URLS = 500;
  const router = useRouter();

  // Check auth on mount & fetch quota
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.push("/login");
      return;
    }
    urlApi.list(token).then((urls) => setUrlCount(urls.length)).catch(() => {});
  }, [router]);

  // Fetch URL preview when URL changes
  useEffect(() => {
    const fetchPreview = async () => {
      if (!url || !isValidUrl(url)) {
        setPreview(null);
        return;
      }

      setIsLoadingPreview(true);
      try {
        const previewData = await urlApi.preview(url);
        setPreview(previewData);
      } catch {
        setPreview(null);
      } finally {
        setIsLoadingPreview(false);
      }
    };

    const debounce = setTimeout(fetchPreview, 500);
    return () => clearTimeout(debounce);
  }, [url]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setResult(null);

    if (!isValidUrl(url)) {
      setError("Please enter a valid URL");
      return;
    }

    const token = localStorage.getItem("access_token");
    if (!token) {
      router.push("/login");
      return;
    }

    setIsLoading(true);
    try {
      const response = await urlApi.shorten(
        url,
        {
          customAlias: customAlias || undefined,
          expirationDays: expirationDays ? Number(expirationDays) : undefined,
          skipAiAnalysis,
          useAiSuggestedAlias: useAiSuggestedAlias && !customAlias,
        },
        token
      );
      setResult({
        shortUrl: response.short_url,
        shortCode: response.short_code,
        ai: response.ai,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to shorten URL");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = async () => {
    if (result) {
      await copyToClipboard(result.shortUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleReset = () => {
    setUrl("");
    setCustomAlias("");
    setExpirationDays("");
    setResult(null);
    setError(null);
    setPreview(null);
    setSkipAiAnalysis(false);
    setUseAiSuggestedAlias(false);
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] py-12 px-4">
      <div className="max-w-2xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Card className="backdrop-blur-sm bg-card/95">
            <CardHeader className="text-center">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.2, type: "spring" }}
                className="mx-auto w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-4"
              >
                <Brain className="w-8 h-8 text-primary" />
              </motion.div>
              <CardTitle className="text-2xl font-bold">AI-Powered URL Shortener</CardTitle>
              <CardDescription>
                Transform URLs with intelligent content analysis, auto-tagging, and smart alias suggestions
              </CardDescription>
            </CardHeader>
            <CardContent>
              <AnimatePresence mode="wait">
                {!result ? (
                  <motion.form
                    key="form"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    onSubmit={handleSubmit}
                    className="space-y-6"
                  >
                    {error && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: "auto" }}
                        className="flex items-center gap-2 p-3 text-sm text-destructive bg-destructive/10 rounded-lg"
                      >
                        <AlertCircle className="w-4 h-4 flex-shrink-0" />
                        <span>{error}</span>
                      </motion.div>
                    )}

                    {/* URL Input */}
                    <div className="space-y-2">
                      <Label htmlFor="url">URL to Shorten</Label>
                      <div className="relative">
                        <Link2 className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                        <Input
                          id="url"
                          type="url"
                          placeholder="https://example.com/your/long/url"
                          value={url}
                          onChange={(e) => setUrl(e.target.value)}
                          className="pl-10"
                          required
                          disabled={isLoading}
                        />
                      </div>
                    </div>

                    {/* URL Preview */}
                    <AnimatePresence>
                      {(preview || isLoadingPreview) && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: "auto" }}
                          exit={{ opacity: 0, height: 0 }}
                          className="overflow-hidden"
                        >
                          <Card className="bg-secondary/50">
                            <CardContent className="p-4">
                              {isLoadingPreview ? (
                                <div className="flex items-center justify-center py-4">
                                  <Spinner size="sm" />
                                  <span className="ml-2 text-sm text-muted-foreground">
                                    Loading preview...
                                  </span>
                                </div>
                              ) : preview ? (
                                <div className="flex gap-4">
                                  {preview.image ? (
                                    <div className="flex-shrink-0 w-20 h-20 rounded-lg bg-muted flex items-center justify-center overflow-hidden">
                                      <img
                                        src={preview.image}
                                        alt=""
                                        className="w-full h-full object-cover"
                                      />
                                    </div>
                                  ) : (
                                    <div className="flex-shrink-0 w-20 h-20 rounded-lg bg-muted flex items-center justify-center">
                                      <ImageIcon className="w-8 h-8 text-muted-foreground" />
                                      {/* Placeholder: PNG, 80x80, generic website preview icon in muted blue */}
                                    </div>
                                  )}
                                  <div className="flex-1 min-w-0">
                                    <h4 className="font-medium truncate">
                                      {preview.title || "No title available"}
                                    </h4>
                                    <p className="text-sm text-muted-foreground line-clamp-2 mt-1">
                                      {preview.description || "No description available"}
                                    </p>
                                  </div>
                                </div>
                              ) : null}
                            </CardContent>
                          </Card>
                        </motion.div>
                      )}
                    </AnimatePresence>

                    {/* Custom Alias */}
                    <div className="space-y-2">
                      <Label htmlFor="alias">Custom Alias (Optional)</Label>
                      <div className="relative">
                        <Sparkles className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                        <Input
                          id="alias"
                          type="text"
                          placeholder="my-custom-link"
                          value={customAlias}
                          onChange={(e) => setCustomAlias(e.target.value)}
                          className="pl-10"
                          disabled={isLoading}
                          pattern="^[a-zA-Z0-9_-]+$"
                          minLength={4}
                          maxLength={20}
                        />
                      </div>
                      <p className="text-xs text-muted-foreground">
                        4-20 characters, letters, numbers, dashes, and underscores only
                      </p>
                    </div>

                    {/* Expiration */}
                    <div className="space-y-2">
                      <Label htmlFor="expiration">Expiration (Optional)</Label>
                      <div className="relative">
                        <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                        <select
                          id="expiration"
                          value={expirationDays}
                          onChange={(e) => setExpirationDays(e.target.value ? Number(e.target.value) : "")}
                          className="w-full h-10 pl-10 pr-3 rounded-md border border-input bg-background text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring"
                          disabled={isLoading}
                        >
                          <option value="">Never expires</option>
                          <option value="1">1 day</option>
                          <option value="7">7 days</option>
                          <option value="30">30 days</option>
                          <option value="90">90 days</option>
                          <option value="365">1 year</option>
                        </select>
                      </div>
                    </div>

                    {/* AI Options */}
                    <div className="space-y-3 p-4 rounded-lg bg-primary/5 border border-primary/10">
                      <div className="flex items-center gap-2 mb-2">
                        <Brain className="w-4 h-4 text-primary" />
                        <span className="text-sm font-medium">AI Analysis Options</span>
                      </div>

                      <label className="flex items-center gap-3 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={useAiSuggestedAlias}
                          onChange={(e) => setUseAiSuggestedAlias(e.target.checked)}
                          disabled={isLoading || !!customAlias}
                          className="w-4 h-4 rounded border-input text-primary focus:ring-primary"
                        />
                        <div className="flex items-center gap-2">
                          <Wand2 className="w-4 h-4 text-muted-foreground" />
                          <span className="text-sm">Use AI-suggested alias</span>
                        </div>
                      </label>
                      {customAlias && (
                        <p className="text-xs text-muted-foreground ml-7">
                          Disabled when custom alias is set
                        </p>
                      )}

                      <label className="flex items-center gap-3 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={skipAiAnalysis}
                          onChange={(e) => {
                            setSkipAiAnalysis(e.target.checked);
                            if (e.target.checked) {
                              setUseAiSuggestedAlias(false);
                            }
                          }}
                          disabled={isLoading}
                          className="w-4 h-4 rounded border-input text-primary focus:ring-primary"
                        />
                        <span className="text-sm text-muted-foreground">Skip AI analysis (faster)</span>
                      </label>
                    </div>

                    {/* Quota Warning */}
                    {urlCount / MAX_URLS >= 0.8 && (
                      <div className={`flex items-center gap-2 p-3 text-sm rounded-lg ${
                        urlCount >= MAX_URLS
                          ? "text-destructive bg-destructive/10"
                          : "text-yellow-600 dark:text-yellow-400 bg-yellow-500/10"
                      }`}>
                        <AlertTriangle className="w-4 h-4 flex-shrink-0" />
                        <span>
                          {urlCount >= MAX_URLS
                            ? `URL quota reached (${urlCount}/${MAX_URLS}). Delete some URLs to create new ones.`
                            : `Approaching URL quota: ${urlCount}/${MAX_URLS} used.`}
                        </span>
                      </div>
                    )}

                    <Button
                      type="submit"
                      variant="gradient"
                      className="w-full"
                      disabled={isLoading || !url || urlCount >= MAX_URLS}
                    >
                      {isLoading ? (
                        <>
                          <Spinner size="sm" className="mr-2" />
                          {skipAiAnalysis ? "Shortening..." : "Analyzing & Shortening..."}
                        </>
                      ) : (
                        <>
                          {skipAiAnalysis ? (
                            <Link2 className="w-4 h-4 mr-2" />
                          ) : (
                            <Brain className="w-4 h-4 mr-2" />
                          )}
                          {skipAiAnalysis ? "Shorten URL" : "Analyze & Shorten"}
                        </>
                      )}
                    </Button>
                  </motion.form>
                ) : (
                  <motion.div
                    key="result"
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0 }}
                    className="space-y-6"
                  >
                    {/* Success animation */}
                    <div className="text-center">
                      <motion.div
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ type: "spring", delay: 0.2 }}
                        className="mx-auto w-16 h-16 rounded-full bg-green-500/10 flex items-center justify-center mb-4"
                      >
                        <Check className="w-8 h-8 text-green-500" />
                      </motion.div>
                      <h3 className="text-xl font-semibold">URL Shortened!</h3>
                      <p className="text-muted-foreground mt-1">
                        Your short link is ready to use
                      </p>
                    </div>

                    {/* Short URL display */}
                    <div className="p-4 rounded-lg bg-secondary/50 space-y-3">
                      <div className="flex items-center gap-2">
                        <Input
                          value={result.shortUrl}
                          readOnly
                          className="font-mono text-sm"
                        />
                        <Button
                          variant={copied ? "default" : "outline"}
                          size="icon"
                          onClick={handleCopy}
                          className="flex-shrink-0"
                        >
                          {copied ? (
                            <Check className="w-4 h-4" />
                          ) : (
                            <Copy className="w-4 h-4" />
                          )}
                        </Button>
                        <Button
                          variant="outline"
                          size="icon"
                          onClick={() => window.open(result.shortUrl, "_blank")}
                          className="flex-shrink-0"
                        >
                          <ExternalLink className="w-4 h-4" />
                        </Button>
                      </div>
                      {copied && (
                        <motion.p
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          className="text-sm text-green-500 text-center"
                        >
                          Copied to clipboard!
                        </motion.p>
                      )}
                    </div>

                    {/* QR Code */}
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.25 }}
                      className="flex flex-col items-center gap-3 p-4 rounded-lg bg-secondary/50"
                    >
                      <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                        <QrCode className="w-4 h-4" />
                        QR Code
                      </div>
                      <div className="bg-white p-3 rounded-lg">
                        <img
                          src={urlApi.qrCodeUrl(result.shortCode)}
                          alt={`QR code for ${result.shortCode}`}
                          className="w-36 h-36"
                        />
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          const a = document.createElement("a");
                          a.href = urlApi.qrCodeUrl(result.shortCode);
                          a.download = `${result.shortCode}-qr.png`;
                          a.click();
                        }}
                      >
                        <Download className="w-4 h-4 mr-1" />
                        Download QR
                      </Button>
                    </motion.div>

                    {/* AI Analysis Results */}
                    {result.ai?.analyzed && (
                      <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3 }}
                        className="p-4 rounded-lg bg-primary/5 border border-primary/10 space-y-4"
                      >
                        <div className="flex items-center gap-2">
                          <Brain className="w-5 h-5 text-primary" />
                          <h4 className="font-semibold">AI Analysis</h4>
                        </div>

                        {/* AI Summary */}
                        {result.ai.summary && (
                          <motion.div
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: 0.4 }}
                            className="space-y-1"
                          >
                            <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                              <FileText className="w-4 h-4" />
                              <span>Summary</span>
                            </div>
                            <p className="text-sm pl-6">{result.ai.summary}</p>
                          </motion.div>
                        )}

                        {/* AI Tags */}
                        {result.ai.tags && result.ai.tags.length > 0 && (
                          <motion.div
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: 0.5 }}
                            className="space-y-2"
                          >
                            <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                              <Tag className="w-4 h-4" />
                              <span>Tags</span>
                            </div>
                            <div className="flex flex-wrap gap-2 pl-6">
                              {result.ai.tags.map((tag, index) => (
                                <motion.span
                                  key={tag}
                                  initial={{ opacity: 0, scale: 0.8 }}
                                  animate={{ opacity: 1, scale: 1 }}
                                  transition={{ delay: 0.5 + index * 0.1 }}
                                  className="px-2 py-1 text-xs font-medium rounded-full bg-primary/10 text-primary border border-primary/20"
                                >
                                  {tag}
                                </motion.span>
                              ))}
                            </div>
                          </motion.div>
                        )}

                        {/* AI Suggested Alias */}
                        {result.ai.suggested_alias && (
                          <motion.div
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: 0.6 }}
                            className="space-y-1"
                          >
                            <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                              <Wand2 className="w-4 h-4" />
                              <span>Suggested Alias</span>
                            </div>
                            <p className="text-sm pl-6 font-mono text-primary">
                              {result.ai.suggested_alias}
                            </p>
                          </motion.div>
                        )}
                      </motion.div>
                    )}

                    {/* Actions */}
                    <div className="flex gap-3">
                      <Button
                        variant="outline"
                        className="flex-1"
                        onClick={handleReset}
                      >
                        Shorten Another
                      </Button>
                      <Button
                        variant="gradient"
                        className="flex-1"
                        onClick={() => router.push("/dashboard")}
                      >
                        View Dashboard
                      </Button>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
