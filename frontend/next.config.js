/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  images: {
    unoptimized: true, // Required for static exports
    domains: ['localhost'],
  },
  trailingSlash: true, // Optional: adds trailing slashes to URLs
}

module.exports = nextConfig