// ── Environment ──────────────────────────────────────────────────────────────

export interface Env {
  REVIEW_CACHE: KVNamespace;
  FIRECRAWL_API_KEY: string;
  ANTHROPIC_API_KEY: string;
  ENVIRONMENT: string;
}

// ── Detection ────────────────────────────────────────────────────────────────

export type ReviewApp =
  | 'judgeme'
  | 'yotpo'
  | 'stamped'
  | 'loox'
  | 'okendo'
  | 'unknown';

export type Platform = 'shopify' | 'unknown';

export interface DetectionResult {
  platform: Platform;
  reviewApp: ReviewApp;
  confidence: number;
  signals: string[];
}

// ── Extraction ───────────────────────────────────────────────────────────────

export interface RawReview {
  productTitle: string;
  productHandle: string;
  rating: number;
  title: string;
  body: string;
  verified: boolean;
  createdAt: string;
  reviewerName: string;
}

export interface ProductReviewSummary {
  productTitle: string;
  productHandle: string;
  averageRating: number;
  totalReviews: number;
  verifiedPercentage: number;
  ratingDistribution: Record<number, number>;
  reviews: RawReview[];
}

// ── Compression / Output ─────────────────────────────────────────────────────

export type OutputFormat = 'standard' | 'min' | 'detailed' | 'json';

export interface CompressedResult {
  domain: string;
  overallRating: number;
  totalReviews: number;
  verifiedPercentage: number;
  markdown: string;
}

// ── Routing ──────────────────────────────────────────────────────────────────

export interface ParsedRequest {
  domain: string;
  productHandle: string | null;
  format: OutputFormat;
}

// ── Extractor interface ──────────────────────────────────────────────────────

export interface ReviewExtractor {
  name: string;
  detect(domain: string, pageContent: string): boolean;
  extract(domain: string, env: Env): Promise<ProductReviewSummary[]>;
}

// ── Firecrawl ────────────────────────────────────────────────────────────────

export interface FirecrawlScrapeResult {
  success: boolean;
  data?: {
    markdown?: string;
    html?: string;
    metadata?: Record<string, string>;
  };
  error?: string;
}
