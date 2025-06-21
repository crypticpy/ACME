/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  basePath: process.env.NODE_ENV === 'production' ? '/acme-cultural-funding-2025' : '',
  images: {
    unoptimized: true,
  },
  reactStrictMode: true,
  swcMinify: true,
  webpack: (config) => {
    // Handle CSV/JSON imports
    config.module.rules.push({
      test: /\.(csv|json)$/,
      loader: 'raw-loader',
    });
    return config;
  },
}

module.exports = nextConfig