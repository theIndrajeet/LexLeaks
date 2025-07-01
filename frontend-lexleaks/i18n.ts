import {notFound} from 'next/navigation';
import {getRequestConfig} from 'next-intl/server';

// Can be imported from a shared config
export const locales = ['en', 'es', 'fr', 'de', 'pt', 'it', 'ru', 'zh', 'ja', 'ar'] as const;
export type Locale = (typeof locales)[number];

export const defaultLocale: Locale = 'en';

export const localeNames: Record<Locale, string> = {
  en: 'English',
  es: 'Español',
  fr: 'Français', 
  de: 'Deutsch',
  pt: 'Português',
  it: 'Italiano',
  ru: 'Русский',
  zh: '中文',
  ja: '日本語',
  ar: 'العربية'
};

export default getRequestConfig(async ({locale}) => {
  // Validate that the incoming `locale` parameter is valid
  const typedLocale = locale as Locale;
  if (!locales.includes(typedLocale)) notFound();

  return {
    locale: typedLocale,
    messages: (await import(`./messages/${typedLocale}.json`)).default
  };
}); 