"use client";

import "./globals.css"; // Import global styles
import Sidebar from "./components/Sidebar";
import Topbar from "./components/Topbar";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="flex h-screen">
        {/* Left Sidebar */}
        <Sidebar />

        {/* Main Content */}
        <div className="flex flex-col flex-1">
          {/* Top Navigation */}
          <Topbar />

          {/* Page Content */}
          <main className="flex-1 bg-gray-50 p-6">{children}</main>
        </div>
      </body>
    </html>
  );
}