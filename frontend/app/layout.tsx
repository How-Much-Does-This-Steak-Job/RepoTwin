import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "RepoTwin by Bob",
  description: "Simulate the blast radius of a code change before writing code",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}

// Made with Bob
