import "./globals.css";
import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "ClariFi — Claim Adjudication DSS",
  description: "Decision Support System for Health Insurance Claim Adjudication",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gray-50 min-h-screen">
        <div className="flex">
          {/* Sidebar */}
          <aside className="w-64 bg-brand-900 min-h-screen fixed flex flex-col">
            {/* Logo & Brand */}
            <div className="p-5 border-b border-brand-800">
              <div>
                <h1 className="text-2xl font-bold leading-tight">
                  <span className="text-orange-400">C</span><span className="text-[#29B5E8]">lariFi</span>
                </h1>
                <p className="text-[11px] text-white mt-0.5">Claim Adjudication with clarity</p>
              </div>
              <p className="text-xs text-brand-400 mt-2">PT Asuransi Sejahtera Medika</p>
            </div>

            {/* Navigation */}
            <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
              <NavLink href="/" label="Dashboard" icon="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />

              <div className="pt-4 pb-1 px-3 text-[10px] font-semibold text-brand-400 uppercase tracking-wider">Claims</div>
              <NavLink href="/claims" label="Claims" icon="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              <NavLink href="/claims/new" label="New Claim" icon="M12 4v16m8-8H4" />

              <div className="pt-4 pb-1 px-3 text-[10px] font-semibold text-brand-400 uppercase tracking-wider">Master Data</div>
              <NavLink href="/policyholders" label="Policyholders" icon="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
              <NavLink href="/policies" label="Policies" icon="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              <NavLink href="/rules" label="Claim Rules" icon="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />

              <div className="pt-4 pb-1 px-3 text-[10px] font-semibold text-brand-400 uppercase tracking-wider">Tools</div>
              <NavLink href="/import" label="Import Documents" icon="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </nav>

            {/* Footer */}
            <div className="p-4 border-t border-brand-800">
              <p className="text-[10px] text-brand-500">Developed by</p>
              <p className="text-sm font-medium">
                <span className="text-gray-400">Dat</span><span className="text-orange-400">A</span><span className="text-gray-400">s</span><span className="text-orange-400">i</span><span className="text-gray-400">a</span>
              </p>
            </div>
          </aside>

          {/* Main content */}
          <main className="ml-64 flex-1 p-8 min-h-screen">{children}</main>
        </div>
      </body>
    </html>
  );
}

function NavLink({ href, label, icon }: { href: string; label: string; icon: string }) {
  return (
    <Link
      href={href}
      className="flex items-center gap-3 px-3 py-2 rounded-lg text-brand-200 hover:bg-brand-800 hover:text-white transition-colors text-sm"
    >
      <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d={icon} />
      </svg>
      {label}
    </Link>
  );
}
