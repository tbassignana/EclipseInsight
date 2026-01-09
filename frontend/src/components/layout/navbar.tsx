"use client";

import Link from "next/link";
import { useTheme } from "next-themes";
import { motion } from "framer-motion";
import { Sun, Moon, Menu, X, Link2, LayoutDashboard, LogIn, UserPlus, Shield, LogOut } from "lucide-react";
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { useAuthContext } from "@/context/AuthContext";

interface NavItem {
  label: string;
  href: string;
  icon?: React.ReactNode;
  authRequired?: boolean;
  adminOnly?: boolean;
}

const navItems: NavItem[] = [
  { label: "Home", href: "/" },
  { label: "Shorten", href: "/shorten", icon: <Link2 className="w-4 h-4" />, authRequired: true },
  { label: "Admin", href: "/admin", icon: <Shield className="w-4 h-4" />, authRequired: true, adminOnly: true },
];

export function Navbar() {
  const { theme, setTheme } = useTheme();
  const { isAuthenticated, user, logout } = useAuthContext();
  const [mounted, setMounted] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Hydration fix - only render full navbar after mount
  // This is a standard Next.js pattern for handling hydration mismatches
  useEffect(() => {
    setMounted(true);
  }, []);

  const isLoggedIn = isAuthenticated;
  const isAdmin = user?.is_admin || false;

  // Return a skeleton during SSR to avoid hydration mismatch
  if (!mounted) {
    return (
      <nav className="fixed top-0 left-0 right-0 z-50 glass h-16" />
    );
  }

  const toggleTheme = () => {
    setTheme(theme === "dark" ? "light" : "dark");
  };

  const handleLogout = () => {
    logout();
    setMobileMenuOpen(false);
  };

  return (
    <motion.nav
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ type: "spring", stiffness: 100, damping: 20 }}
      className="fixed top-0 left-0 right-0 z-50 glass"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2">
            <motion.div
              whileHover={{ scale: 1.05 }}
              className="text-2xl font-bold bg-gradient-to-r from-red-600 to-red-800 bg-clip-text text-transparent"
            >
              Eclipse<span className="text-primary">Insight</span>
            </motion.div>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-4">
            {navItems.map((item) => {
              if (item.authRequired && !isLoggedIn) return null;
              if (item.adminOnly && !isAdmin) return null;
              return (
                <Link key={item.href} href={item.href}>
                  <motion.div
                    whileHover={{ scale: 1.05 }}
                    className="flex items-center space-x-1 px-3 py-2 rounded-lg text-sm font-medium text-foreground/80 hover:text-foreground hover:bg-secondary transition-colors"
                  >
                    {item.icon}
                    <span>{item.label}</span>
                  </motion.div>
                </Link>
              );
            })}

            {/* Auth Buttons */}
            {!isLoggedIn ? (
              <div className="flex items-center space-x-2">
                <Link href="/login">
                  <Button variant="ghost" size="sm">
                    <LogIn className="w-4 h-4 mr-1" />
                    Login
                  </Button>
                </Link>
                <Link href="/register">
                  <Button variant="gradient" size="sm">
                    <UserPlus className="w-4 h-4 mr-1" />
                    Sign Up
                  </Button>
                </Link>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <Link href="/dashboard">
                  <Button variant="gradient" size="sm">
                    <LayoutDashboard className="w-4 h-4 mr-1" />
                    Dashboard
                  </Button>
                </Link>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleLogout}
                >
                  <LogOut className="w-4 h-4 mr-1" />
                  Logout
                </Button>
              </div>
            )}

            {/* Theme Toggle */}
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={toggleTheme}
              className="p-2 rounded-lg bg-secondary hover:bg-secondary/80 transition-colors"
              aria-label="Toggle theme"
            >
              {theme === "dark" ? (
                <Sun className="w-5 h-5" />
              ) : (
                <Moon className="w-5 h-5" />
              )}
            </motion.button>
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden flex items-center space-x-2">
            <motion.button
              whileTap={{ scale: 0.9 }}
              onClick={toggleTheme}
              className="p-2 rounded-lg bg-secondary"
            >
              {theme === "dark" ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </motion.button>
            <motion.button
              whileTap={{ scale: 0.9 }}
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-lg bg-secondary"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </motion.button>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden pb-4"
          >
            <div className="flex flex-col space-y-2">
              {navItems.map((item) => {
                if (item.authRequired && !isLoggedIn) return null;
                if (item.adminOnly && !isAdmin) return null;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className="flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium hover:bg-secondary transition-colors"
                  >
                    {item.icon}
                    <span>{item.label}</span>
                  </Link>
                );
              })}
              {!isLoggedIn ? (
                <>
                  <Link href="/login" onClick={() => setMobileMenuOpen(false)}>
                    <Button variant="ghost" className="w-full justify-start">
                      <LogIn className="w-4 h-4 mr-2" />
                      Login
                    </Button>
                  </Link>
                  <Link href="/register" onClick={() => setMobileMenuOpen(false)}>
                    <Button variant="gradient" className="w-full">
                      <UserPlus className="w-4 h-4 mr-2" />
                      Sign Up
                    </Button>
                  </Link>
                </>
              ) : (
                <>
                  <Link href="/dashboard" onClick={() => setMobileMenuOpen(false)}>
                    <Button variant="gradient" className="w-full">
                      <LayoutDashboard className="w-4 h-4 mr-2" />
                      Dashboard
                    </Button>
                  </Link>
                  <Button
                    variant="ghost"
                    className="w-full justify-start"
                    onClick={handleLogout}
                  >
                    <LogOut className="w-4 h-4 mr-2" />
                    Logout
                  </Button>
                </>
              )}
            </div>
          </motion.div>
        )}
      </div>
    </motion.nav>
  );
}
