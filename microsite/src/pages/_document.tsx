import { Html, Head, Main, NextScript } from 'next/document'

export default function Document() {
  return (
    <Html lang="en">
      <Head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
        <meta name="theme-color" content="#1a365d" />
        <meta
          name="description"
          content="Comprehensive analysis of Austin's cultural funding landscape with insights from community feedback."
        />
        <meta property="og:title" content="ACME Cultural Funding Analysis 2025" />
        <meta
          property="og:description"
          content="Explore data-driven insights on Austin's arts, culture, music, and entertainment funding."
        />
        <meta property="og:type" content="website" />
        <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
        <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
      </Head>
      <body>
        <Main />
        <NextScript />
      </body>
    </Html>
  )
}