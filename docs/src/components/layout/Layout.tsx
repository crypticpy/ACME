import { ReactNode } from 'react'
import Head from 'next/head'
import Navigation from './Navigation'
import Footer from './Footer'

interface LayoutProps {
  children: ReactNode
  title?: string
  description?: string
}

const Layout = ({ 
  children, 
  title = 'ACME Cultural Funding Analysis 2025',
  description = 'Comprehensive analysis of Austin\'s cultural funding landscape'
}: LayoutProps) => {
  return (
    <>
      <Head>
        <title>{title}</title>
        <meta name="description" content={description} />
      </Head>
      <div className="min-h-screen flex flex-col">
        <Navigation />
        <main className="flex-grow">
          {children}
        </main>
        <Footer />
      </div>
    </>
  )
}

export default Layout