import {useTranslations} from 'next-intl'
import LanguageSelector from '@/components/LanguageSelector'
import Link from 'next/link'

export default function I18nDemoPage() {
  const t = useTranslations('HomePage')
  const tSearch = useTranslations('SearchFilter')
  const tImpact = useTranslations('ImpactTracker')
  const tCategories = useTranslations('Categories')

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-12">
      <div className="max-w-4xl mx-auto px-4">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
          {/* Header */}
          <div className="flex justify-between items-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
              i18n Demo - Internationalization
            </h1>
            <LanguageSelector />
          </div>

          {/* Navigation Example */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-gray-200">
              Navigation Items:
            </h2>
            <div className="flex gap-4 flex-wrap">
              <span className="px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded">
                {t('nav.home')}
              </span>
              <span className="px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded">
                {t('nav.about')}
              </span>
              <span className="px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded">
                {t('nav.archive')}
              </span>
              <span className="px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded">
                {t('nav.submitLeak')}
              </span>
            </div>
          </div>

          {/* Title and Subtitle */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-gray-200">
              Main Headlines:
            </h2>
            <div className="space-y-2">
              <p className="text-3xl font-bold">{t('title')}</p>
              <p className="text-xl text-gray-600 dark:text-gray-400">{t('subtitle')}</p>
            </div>
          </div>

          {/* Search Component Translations */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-gray-200">
              Search Component:
            </h2>
            <div className="space-y-2">
              <p><strong>Placeholder:</strong> {tSearch('searchPlaceholder')}</p>
              <p><strong>Button:</strong> {tSearch('search')} / {tSearch('searching')}</p>
              <p><strong>Sort Options:</strong> {tSearch('newestFirst')}, {tSearch('oldestFirst')}, {tSearch('mostRelevant')}</p>
            </div>
          </div>

          {/* Impact Tracker Translations */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-gray-200">
              Impact Tracker:
            </h2>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded">
                <p className="font-semibold">{tImpact('legalActions')}</p>
              </div>
              <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded">
                <p className="font-semibold">{tImpact('investigations')}</p>
              </div>
              <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded">
                <p className="font-semibold">{tImpact('policyChanges')}</p>
              </div>
              <div className="bg-orange-50 dark:bg-orange-900/20 p-4 rounded">
                <p className="font-semibold">{tImpact('completed')}</p>
              </div>
            </div>
          </div>

          {/* Categories */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-gray-200">
              Categories:
            </h2>
            <div className="flex flex-wrap gap-2">
              <span className="px-3 py-1 bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 rounded-full text-sm">
                {tCategories('corporate')}
              </span>
              <span className="px-3 py-1 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 rounded-full text-sm">
                {tCategories('criminal')}
              </span>
              <span className="px-3 py-1 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300 rounded-full text-sm">
                {tCategories('judicial')}
              </span>
              <span className="px-3 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 rounded-full text-sm">
                {tCategories('ethics')}
              </span>
            </div>
          </div>

          {/* Back Link */}
          <div className="mt-8 pt-8 border-t border-gray-200 dark:border-gray-700">
            <Link
              href="/"
              className="text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300"
            >
              ← Back to Home
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
} 