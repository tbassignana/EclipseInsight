"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { Shield, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function PrivacyPolicyPage() {
  return (
    <div className="min-h-[calc(100vh-4rem)] py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          {/* Header */}
          <div className="mb-8">
            <Link href="/register">
              <Button variant="ghost" size="sm" className="mb-4">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Registration
              </Button>
            </Link>
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
                <Shield className="w-6 h-6 text-primary" />
              </div>
              <div>
                <h1 className="text-3xl font-bold">Privacy Policy</h1>
                <p className="text-muted-foreground">Last updated: January 2026</p>
              </div>
            </div>
            <div className="p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
              <p className="text-sm text-yellow-600 dark:text-yellow-400">
                <strong>Demonstration Only:</strong> This is a sample Privacy Policy for demonstration purposes.
                Do not use this as legal advice. Consult with a legal professional for actual privacy policies.
              </p>
            </div>
          </div>

          {/* Content */}
          <div className="prose prose-neutral dark:prose-invert max-w-none space-y-8">
            <section>
              <h2 className="text-xl font-semibold mb-3">1. Introduction</h2>
              <p className="text-muted-foreground leading-relaxed">
                EclipseInsight (&quot;we&quot;, &quot;our&quot;, or &quot;us&quot;) is committed to protecting your privacy. This Privacy Policy
                explains how we collect, use, disclose, and safeguard your information when you use our AI-powered
                URL shortening and content analysis service.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-3">2. Information We Collect</h2>

              <h3 className="text-lg font-medium mt-4 mb-2">Personal Information</h3>
              <ul className="list-disc list-inside text-muted-foreground space-y-2">
                <li>Email address (for account registration)</li>
                <li>Password (stored securely using encryption)</li>
                <li>Account preferences and settings</li>
              </ul>

              <h3 className="text-lg font-medium mt-4 mb-2">Usage Information</h3>
              <ul className="list-disc list-inside text-muted-foreground space-y-2">
                <li>URLs you shorten through our service</li>
                <li>Click data and analytics for your shortened links</li>
                <li>IP addresses of visitors who click your links</li>
                <li>Browser type, device information, and operating system</li>
                <li>Geographic location (country/region level)</li>
                <li>Referrer information (where clicks originate from)</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-3">3. How We Use Your Information</h2>
              <p className="text-muted-foreground leading-relaxed mb-3">
                We use the collected information to:
              </p>
              <ul className="list-disc list-inside text-muted-foreground space-y-2">
                <li>Provide and maintain our AI-powered URL shortening service</li>
                <li>Analyze linked content using AI to generate tags, summaries, and suggested aliases</li>
                <li>Detect and filter potentially harmful or toxic content</li>
                <li>Generate analytics and insights for your shortened links</li>
                <li>Improve and optimize our AI models and service</li>
                <li>Communicate with you about your account</li>
                <li>Detect and prevent fraud or abuse</li>
                <li>Comply with legal obligations</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-3">3a. AI Processing</h2>
              <p className="text-muted-foreground leading-relaxed mb-3">
                Our service uses Anthropic&apos;s Claude AI to analyze content from URLs you submit. This processing includes:
              </p>
              <ul className="list-disc list-inside text-muted-foreground space-y-2">
                <li>Fetching and analyzing publicly available content from submitted URLs</li>
                <li>Generating descriptive tags and summaries based on content</li>
                <li>Suggesting memorable aliases based on content meaning</li>
                <li>Evaluating content for potential toxicity or harmful material</li>
              </ul>
              <p className="text-muted-foreground leading-relaxed mt-3">
                Content sent for AI analysis is processed in accordance with Anthropic&apos;s data handling policies.
                We do not use your data to train AI models.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-3">4. Data Sharing and Disclosure</h2>
              <p className="text-muted-foreground leading-relaxed mb-3">
                We do not sell your personal information. We may share your information in the following circumstances:
              </p>
              <ul className="list-disc list-inside text-muted-foreground space-y-2">
                <li><strong>Service Providers:</strong> Third-party services that help us operate our platform</li>
                <li><strong>Legal Requirements:</strong> When required by law or to protect our rights</li>
                <li><strong>Business Transfers:</strong> In connection with a merger, acquisition, or sale of assets</li>
                <li><strong>With Your Consent:</strong> When you explicitly authorize us to share information</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-3">5. Data Security</h2>
              <p className="text-muted-foreground leading-relaxed">
                We implement industry-standard security measures to protect your information, including:
              </p>
              <ul className="list-disc list-inside text-muted-foreground space-y-2 mt-3">
                <li>SSL/TLS encryption for data in transit</li>
                <li>Secure password hashing using bcrypt</li>
                <li>Regular security audits and updates</li>
                <li>Access controls and authentication</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-3">6. Data Retention</h2>
              <p className="text-muted-foreground leading-relaxed">
                We retain your personal information for as long as your account is active or as needed to provide
                services. Analytics data for shortened URLs is retained according to your account plan. You may
                request deletion of your account and associated data at any time.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-3">7. Your Rights</h2>
              <p className="text-muted-foreground leading-relaxed mb-3">
                Depending on your location, you may have the following rights:
              </p>
              <ul className="list-disc list-inside text-muted-foreground space-y-2">
                <li><strong>Access:</strong> Request a copy of your personal data</li>
                <li><strong>Correction:</strong> Request correction of inaccurate data</li>
                <li><strong>Deletion:</strong> Request deletion of your personal data</li>
                <li><strong>Portability:</strong> Request transfer of your data</li>
                <li><strong>Opt-out:</strong> Opt out of certain data processing activities</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-3">8. Cookies and Tracking</h2>
              <p className="text-muted-foreground leading-relaxed">
                We use cookies and similar technologies to maintain your session, remember your preferences,
                and analyze usage patterns. You can control cookie settings through your browser preferences.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-3">9. Third-Party Links</h2>
              <p className="text-muted-foreground leading-relaxed">
                Our service may contain links to third-party websites. We are not responsible for the privacy
                practices of these external sites. We encourage you to review the privacy policies of any
                third-party sites you visit.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-3">10. Children&apos;s Privacy</h2>
              <p className="text-muted-foreground leading-relaxed">
                Our service is not intended for children under 13 years of age. We do not knowingly collect
                personal information from children under 13. If you believe we have collected information from
                a child under 13, please contact us immediately.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-3">11. Changes to This Policy</h2>
              <p className="text-muted-foreground leading-relaxed">
                We may update this Privacy Policy from time to time. We will notify you of significant changes
                by posting a notice on our website or sending an email to registered users. Your continued use
                of the service after changes constitutes acceptance of the updated policy.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-3">12. Contact Us</h2>
              <p className="text-muted-foreground leading-relaxed">
                If you have questions or concerns about this Privacy Policy or our data practices, please contact us at:{" "}
                <a href="mailto:privacy@eclipseinsight.com" className="text-primary hover:underline">
                  privacy@eclipseinsight.com
                </a>
              </p>
            </section>
          </div>

          {/* Footer */}
          <div className="mt-12 pt-8 border-t border-border">
            <div className="flex flex-col sm:flex-row gap-4 justify-between items-center">
              <p className="text-sm text-muted-foreground">
                Your privacy is important to us. Thank you for trusting EclipseInsight.
              </p>
              <Link href="/register">
                <Button variant="gradient">
                  Create Account
                </Button>
              </Link>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
