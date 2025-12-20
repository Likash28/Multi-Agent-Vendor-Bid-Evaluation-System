export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="w-full max-w-md px-4">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            GovProcure
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Multi-Agent Vendor Bid Evaluation System
          </p>
        </div>
        {children}
      </div>
    </div>
  );
}
