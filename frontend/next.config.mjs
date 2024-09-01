/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
  rewrites: async () => {
    return  [
      {
        source: "/docs",
        destination: "/api/docs",
      },
      {
        source: "/openapi.json",
        destination: "/api/openapi.json",
      },
    ];
  },
};
export default nextConfig;
