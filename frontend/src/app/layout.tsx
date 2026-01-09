import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/providers/theme-provider";
import { AuthProvider } from "@/context/AuthContext";
import { Navbar } from "@/components/layout/navbar";
import { Footer } from "@/components/layout/footer";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: {
    default: "EclipseInsight - AI-Powered URL Shortener",
    template: "%s | EclipseInsight",
  },
  description: "AI-powered URL shortening with intelligent content analysis. Generate tags, summaries, and detect content quality automatically.",
  keywords: ["url shortener", "link shortener", "ai analysis", "content tagging", "click tracking", "short links", "custom urls", "ai-powered"],
  authors: [{ name: "EclipseInsight" }],
  creator: "EclipseInsight",
  metadataBase: new URL(process.env.NEXT_PUBLIC_BASE_URL || "http://localhost:3000"),
  openGraph: {
    title: "EclipseInsight - AI-Powered URL Shortener",
    description: "AI-powered URL shortening with intelligent content analysis. Generate tags, summaries, and detect content quality automatically.",
    type: "website",
    siteName: "EclipseInsight",
    locale: "en_US",
  },
  twitter: {
    card: "summary_large_image",
    title: "EclipseInsight - AI-Powered URL Shortener",
    description: "AI-powered URL shortening with intelligent content analysis",
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  icons: {
    icon: "/favicon.ico",
    shortcut: "/favicon-16x16.png",
    apple: "/apple-touch-icon.png",
  },
  manifest: "/site.webmanifest",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased min-h-screen flex flex-col`}
      >
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem
          disableTransitionOnChange
        >
          <AuthProvider>
            <Navbar />
            <main className="flex-1 pt-16">
              {children}
            </main>
            <Footer />
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
