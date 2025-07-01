import { ReactNode } from 'react'
import {notFound} from 'next/navigation'
import {locales} from '../../i18n'
import {NextIntlClientProvider} from 'next-intl'
import {getMessages} from 'next-intl/server'

export default async function LocaleLayout({
  children,
  params: {locale}
}: {
  children: ReactNode
  params: {locale: string}
}) {
  // Validate that the incoming `locale` parameter is valid
  if (!locales.includes(locale as any)) {
    notFound()
  }

  // Providing all messages to the client
  // side is the easiest way to get started
  const messages = await getMessages()

  return (
    <NextIntlClientProvider messages={messages}>
      {children}
    </NextIntlClientProvider>
  )
} 