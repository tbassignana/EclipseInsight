import { getRequestConfig } from "next-intl/server";

const locales = ["en", "es"] as const;
type Locale = (typeof locales)[number];
const defaultLocale: Locale = "en";

export default getRequestConfig(async ({ requestLocale }) => {
  // Use requestLocale or default to 'en'
  let locale = await requestLocale;

  // Validate locale
  if (!locale || !locales.includes(locale as Locale)) {
    locale = defaultLocale;
  }

  return {
    locale,
    messages: (await import(`../../../messages/${locale}.json`)).default,
  };
});
