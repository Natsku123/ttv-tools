/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    const env = process.env.NODE_ENV
    if (env === "development") {
      return {
        beforeFiles: [
          {
            source: "/api/:path*",
            destination: "http://localhost:8000/:path*"
          }
        ]
      }
    }
    return [];
  }
}

module.exports = nextConfig
