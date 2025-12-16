"use client";

import "./globals.css";
import type { ReactNode } from "react";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <head>
        <title>Prediction Market Arbitrage Detector</title>
        <meta
          name="description"
          content="LLM-assisted, deterministically validated arbitrage detection between Kalshi and Polymarket."
        />
      </head>
      <body>{children}</body>
    </html>
  );
}


