"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Brain, BarChart3, ShieldAlert, Sparkles, Tags, FileText, Clock, Eye, LayoutDashboard } from "lucide-react";
import { useAuthContext } from "@/context/AuthContext";

const features = [
  {
    icon: <Brain className="w-6 h-6" />,
    title: "AI-Powered Analysis",
    description: "Claude AI automatically analyzes your content, extracting key insights and understanding context.",
  },
  {
    icon: <Tags className="w-6 h-6" />,
    title: "Smart Auto-Tagging",
    description: "Get intelligent tags generated from your content to improve organization and discoverability.",
  },
  {
    icon: <FileText className="w-6 h-6" />,
    title: "AI Summaries",
    description: "Receive concise, AI-generated summaries that capture the essence of linked content.",
  },
  {
    icon: <ShieldAlert className="w-6 h-6" />,
    title: "Toxicity Detection",
    description: "Automatic content moderation rejects harmful or toxic links before they're shared.",
  },
  {
    icon: <Sparkles className="w-6 h-6" />,
    title: "Suggested Aliases",
    description: "AI recommends memorable, relevant short aliases based on your content's meaning.",
  },
  {
    icon: <Eye className="w-6 h-6" />,
    title: "Rich Previews",
    description: "Auto-generated visual previews with titles and descriptions for every shortened link.",
  },
  {
    icon: <BarChart3 className="w-6 h-6" />,
    title: "Real-Time Analytics",
    description: "Track clicks, referrers, devices, and geographic data with live dashboards.",
  },
  {
    icon: <Clock className="w-6 h-6" />,
    title: "Smart Expiration",
    description: "Set custom expiration dates for time-sensitive campaigns and temporary shares.",
  },
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
};

export default function Home() {
  const { isAuthenticated } = useAuthContext();

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden py-20 sm:py-32">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-background to-background" />
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/20 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl" />

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center"
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.1 }}
              className="flex justify-center mb-8"
            >
              <img
                src="/EclipseInsight.png"
                alt="EclipseInsight Logo"
                width={800}
                height={300}
                className="h-auto max-w-full drop-shadow-2xl"
              />
            </motion.div>

            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="text-4xl sm:text-6xl lg:text-7xl font-bold tracking-tight"
            >
              <span className="bg-gradient-to-r from-foreground via-primary to-red-400 bg-clip-text text-transparent">
                AI-Powered Link Intelligence
              </span>
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="mt-6 text-lg sm:text-xl text-muted-foreground max-w-3xl mx-auto"
            >
              Transform URLs into intelligent, analyzed links. Get AI-generated tags, summaries,
              and content insights powered by Claude. Detect toxic content automatically and
              track everything with real-time analytics.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="mt-10 flex flex-col sm:flex-row gap-4 justify-center"
            >
              {isAuthenticated ? (
                <>
                  <Link href="/shorten">
                    <Button variant="gradient" size="lg" className="w-full sm:w-auto text-lg px-8 py-6">
                      <Brain className="w-5 h-5 mr-2" />
                      Analyze & Shorten
                    </Button>
                  </Link>
                  <Link href="/dashboard">
                    <Button variant="outline" size="lg" className="w-full sm:w-auto text-lg px-8 py-6">
                      <LayoutDashboard className="w-5 h-5 mr-2" />
                      View Insights
                    </Button>
                  </Link>
                </>
              ) : (
                <>
                  <Link href="/register">
                    <Button variant="gradient" size="lg" className="w-full sm:w-auto text-lg px-8 py-6">
                      <Sparkles className="w-5 h-5 mr-2" />
                      Start Analyzing Free
                    </Button>
                  </Link>
                  <Link href="/login">
                    <Button variant="outline" size="lg" className="w-full sm:w-auto text-lg px-8 py-6">
                      Sign In
                    </Button>
                  </Link>
                </>
              )}
            </motion.div>

            {!isAuthenticated && (
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
                className="mt-4 text-sm text-muted-foreground"
              >
                Powered by Claude AI — No credit card required
              </motion.p>
            )}
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-secondary/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl sm:text-4xl font-bold">
              Intelligent Link Management
            </h2>
            <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
              AI-powered features that understand your content, protect your reputation,
              and deliver actionable insights.
            </p>
          </motion.div>

          <motion.div
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
          >
            {features.map((feature, index) => (
              <motion.div key={index} variants={itemVariants}>
                <Card className="h-full hover:shadow-lg transition-shadow duration-300 hover:border-primary/50">
                  <CardContent className="p-6">
                    <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center text-primary mb-4">
                      {feature.icon}
                    </div>
                    <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                    <p className="text-muted-foreground">{feature.description}</p>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center"
          >
            {[
              { value: "AI", label: "Powered by Claude" },
              { value: "100%", label: "Content Analyzed" },
              { value: "Real-Time", label: "Analytics" },
              { value: "Auto", label: "Toxicity Detection" },
            ].map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.5 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
              >
                <div className="text-4xl sm:text-5xl font-bold bg-gradient-to-r from-primary to-red-400 bg-clip-text text-transparent">
                  {stat.value}
                </div>
                <div className="mt-2 text-muted-foreground">{stat.label}</div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-primary/20 via-primary/10 to-red-500/20" />
        <div className="relative max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              {isAuthenticated ? "Ready to analyze your next link?" : "Ready to unlock AI-powered insights?"}
            </h2>
            <p className="text-lg text-muted-foreground mb-8">
              {isAuthenticated
                ? "Create intelligent short links with AI-generated tags, summaries, and content analysis."
                : "Join EclipseInsight to transform your URLs into intelligent, analyzed links with automatic content understanding."}
            </p>
            <Link href={isAuthenticated ? "/shorten" : "/register"}>
              <Button variant="gradient" size="lg" className="text-lg px-8 py-6">
                <Brain className="w-5 h-5 mr-2" />
                {isAuthenticated ? "Analyze & Create Link" : "Start With AI Analysis"}
              </Button>
            </Link>
          </motion.div>
        </div>
      </section>
    </div>
  );
}
