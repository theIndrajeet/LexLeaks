import createMiddleware from 'next-intl/middleware';
import {locales, defaultLocale} from './i18n';

export default createMiddleware({
  // A list of all locales that are supported
  locales,
  
  // If this locale is matched, pathnames work without a prefix (e.g. `/about`)
  defaultLocale,
  
  // If a locale is detected that's not in locales, redirect to this
  localeDetection: true
});

export const config = {
  // Match only internationalized pathnames
  matcher: ['/', '/(en|es|fr|de|pt|it|ru|zh|ja|ar)/:path*']
}; 