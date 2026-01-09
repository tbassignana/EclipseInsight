"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { Construction, ArrowLeft, Mail, Wrench } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function ForgotPasswordPage() {
  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center px-4 py-12">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        <Card className="backdrop-blur-sm bg-card/95">
          <CardHeader className="space-y-1 text-center">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring" }}
              className="mx-auto w-16 h-16 rounded-full bg-yellow-500/10 flex items-center justify-center mb-4"
            >
              <Construction className="w-8 h-8 text-yellow-500" />
            </motion.div>
            <CardTitle className="text-2xl font-bold">Password Reset</CardTitle>
            <CardDescription>
              This feature is currently under construction
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Under Construction Banner */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-lg"
            >
              <div className="flex items-start gap-3">
                <Wrench className="w-5 h-5 text-yellow-500 mt-0.5 flex-shrink-0" />
                <div>
                  <h3 className="font-medium text-yellow-600 dark:text-yellow-400 mb-1">
                    Feature Under Development
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    We&apos;re working hard to bring you a secure password reset feature.
                    This functionality will be available soon.
                  </p>
                </div>
              </div>
            </motion.div>

            {/* What to expect */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="space-y-3"
            >
              <h4 className="text-sm font-medium">Coming Soon:</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex items-center gap-2">
                  <Mail className="w-4 h-4 text-primary" />
                  Email-based password reset link
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded-full bg-primary/20 flex items-center justify-center">
                    <div className="w-1.5 h-1.5 rounded-full bg-primary" />
                  </div>
                  Secure token verification
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded-full bg-primary/20 flex items-center justify-center">
                    <div className="w-1.5 h-1.5 rounded-full bg-primary" />
                  </div>
                  Password strength validation
                </li>
              </ul>
            </motion.div>

            {/* Progress indicator */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="space-y-2"
            >
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>Development Progress</span>
                <span>In Progress</span>
              </div>
              <div className="h-2 bg-secondary rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: "45%" }}
                  transition={{ delay: 0.6, duration: 1, ease: "easeOut" }}
                  className="h-full bg-gradient-to-r from-primary to-blue-400 rounded-full"
                />
              </div>
            </motion.div>

            {/* Alternative Help */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
              className="p-4 bg-secondary/50 rounded-lg"
            >
              <h4 className="text-sm font-medium mb-2">Need Help Now?</h4>
              <p className="text-sm text-muted-foreground">
                If you&apos;ve forgotten your password and need immediate assistance, please contact our support team at{" "}
                <a href="mailto:support@eclipseurl.com" className="text-primary hover:underline">
                  support@eclipseurl.com
                </a>
              </p>
            </motion.div>

            {/* Back to Login */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.7 }}
              className="pt-4"
            >
              <Link href="/login">
                <Button variant="outline" className="w-full">
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Back to Sign In
                </Button>
              </Link>
            </motion.div>
          </CardContent>
        </Card>

        {/* Additional Info */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="text-center text-sm text-muted-foreground mt-6"
        >
          Don&apos;t have an account?{" "}
          <Link href="/register" className="text-primary hover:underline">
            Create one here
          </Link>
        </motion.p>
      </motion.div>
    </div>
  );
}
