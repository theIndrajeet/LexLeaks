/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  
  images: {
    domains: ['localhost'],
  },
  
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
  
  async rewrites() {
    return [
      {
        source: '/api/proxy/:path*',
        destination: 'https://lexleaks-api-563011146464.asia-south1.run.app/api/:path*',
      },
    ]
  },
}

module.exports = nextConfig 