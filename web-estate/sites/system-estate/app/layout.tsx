import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Keddeh Systems | System Estate",
  description: "Explore the Keddeh Systems Foundry Fabric estate, concrete delivery capabilities and preserved system boundaries.",
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
