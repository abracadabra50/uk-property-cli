import type { Env, ProductReviewSummary, RawReview, ReviewExtractor } from '../types';
import { firecrawlScrape } from './firecrawl';

const JUDGEME_PATTERNS = [/judge\.me/i, /judgeme/i, /jdgm-/i];

function parseRating(text: string): number {
  // Look for star ratings in various formats
  const match = text.match(/(\d(?:\.\d)?)\s*(?:\/\s*5|stars?|★)/i);
  if (match) return parseFloat(match[1]);

  // Count star characters
  const stars = (text.match(/★/g) || []).length;
  if (stars > 0 && stars <= 5) return stars;

  return 0;
}

function parseDate(text: string): string {
  // Try to parse common date formats from review pages
  const dateMatch = text.match(
    /(\d{1,2}[\s/.-]\d{1,2}[\s/.-]\d{2,4}|\w+ \d{1,2},?\s*\d{4}|\d{4}-\d{2}-\d{2})/,
  );
  if (dateMatch) {
    const parsed = new Date(dateMatch[1]);
    if (!isNaN(parsed.getTime())) return parsed.toISOString();
  }
  return new Date().toISOString();
}

function extractReviewsFromMarkdown(markdown: string, domain: string): RawReview[] {
  const reviews: RawReview[] = [];

  // Judge.me review blocks typically have a pattern of:
  // Rating line, reviewer name, date, review title, review body, verified badge
  // The exact format varies by theme, so we use flexible parsing.

  // Split on common review separators
  const blocks = markdown.split(/(?:^|\n)(?:---|___|\*\*\*|#{1,3}\s)/m).filter((b) => b.trim());

  for (const block of blocks) {
    const rating = parseRating(block);
    if (rating === 0) continue; // Not a review block

    const lines = block
      .split('\n')
      .map((l) => l.trim())
      .filter(Boolean);
    if (lines.length < 2) continue;

    const verified = /verified/i.test(block);
    const date = parseDate(block);

    // Try to extract reviewer name (often bold or at start of block)
    const nameMatch = block.match(/\*\*(.+?)\*\*/);
    const reviewerName = nameMatch ? nameMatch[1] : 'Anonymous';

    // Review title is often the first substantial line after rating
    let title = '';
    let body = '';
    let foundRating = false;

    for (const line of lines) {
      if (!foundRating && parseRating(line) > 0) {
        foundRating = true;
        continue;
      }
      if (foundRating && !title && line.length > 5 && line.length < 200) {
        title = line.replace(/\*\*/g, '').trim();
      } else if (foundRating && title) {
        body += (body ? ' ' : '') + line.replace(/\*\*/g, '').trim();
      }
    }

    if (!title && !body) continue;

    reviews.push({
      productTitle: '',
      productHandle: '',
      rating,
      title: title || '(no title)',
      body: body || title,
      verified,
      createdAt: date,
      reviewerName,
    });
  }

  return reviews;
}

function groupReviewsByProduct(reviews: RawReview[]): ProductReviewSummary[] {
  const grouped = new Map<string, RawReview[]>();

  for (const review of reviews) {
    const key = review.productHandle || review.productTitle || '_all';
    if (!grouped.has(key)) grouped.set(key, []);
    grouped.get(key)!.push(review);
  }

  const summaries: ProductReviewSummary[] = [];

  for (const [key, productReviews] of grouped) {
    const ratings = productReviews.map((r) => r.rating);
    const avgRating = ratings.reduce((a, b) => a + b, 0) / ratings.length;
    const verifiedCount = productReviews.filter((r) => r.verified).length;

    const distribution: Record<number, number> = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 };
    for (const r of productReviews) {
      const rounded = Math.round(r.rating);
      if (rounded >= 1 && rounded <= 5) distribution[rounded]++;
    }

    summaries.push({
      productTitle: productReviews[0]?.productTitle || key,
      productHandle: productReviews[0]?.productHandle || key.toLowerCase().replace(/\s+/g, '-'),
      averageRating: Math.round(avgRating * 10) / 10,
      totalReviews: productReviews.length,
      verifiedPercentage: Math.round((verifiedCount / productReviews.length) * 100),
      ratingDistribution: distribution,
      reviews: productReviews,
    });
  }

  return summaries.sort((a, b) => b.totalReviews - a.totalReviews);
}

async function tryJudgeMeApi(domain: string): Promise<RawReview[] | null> {
  // Judge.me has a public-facing reviews page for stores
  // Try the public widget API endpoint
  const url = `https://judge.me/reviews/reviews_for_widget?url=${encodeURIComponent(domain)}&per_page=50&page=1`;

  try {
    const response = await fetch(url, {
      headers: { Accept: 'application/json' },
    });

    if (!response.ok) return null;

    const data = (await response.json()) as {
      reviews?: Array<{
        title?: string;
        body?: string;
        rating?: number;
        reviewer?: { name?: string };
        product_title?: string;
        product_handle?: string;
        verified?: string;
        created_at?: string;
      }>;
    };

    if (!data.reviews || !Array.isArray(data.reviews)) return null;

    return data.reviews.map((r) => ({
      productTitle: r.product_title || '',
      productHandle: r.product_handle || '',
      rating: r.rating || 0,
      title: r.title || '',
      body: r.body || '',
      verified: r.verified === 'buyer',
      createdAt: r.created_at || new Date().toISOString(),
      reviewerName: r.reviewer?.name || 'Anonymous',
    }));
  } catch {
    return null;
  }
}

export async function extractJudgeMeReviews(
  domain: string,
  env: Env,
): Promise<ProductReviewSummary[]> {
  // Strategy 1: Try the Judge.me widget API directly
  const apiReviews = await tryJudgeMeApi(domain);

  if (apiReviews && apiReviews.length > 0) {
    return groupReviewsByProduct(apiReviews);
  }

  // Strategy 2: Scrape the store's all-reviews page via Firecrawl
  const reviewPageUrls = [
    `https://${domain}/pages/reviews`,
    `https://${domain}/apps/judge-me-reviews`,
    `https://${domain}/collections/all`, // Product pages often have inline reviews
  ];

  for (const pageUrl of reviewPageUrls) {
    const result = await firecrawlScrape(pageUrl, env.FIRECRAWL_API_KEY, {
      formats: ['markdown'],
      waitFor: 5000, // Judge.me widgets load via JS
    });

    if (result.success && result.data?.markdown) {
      const reviews = extractReviewsFromMarkdown(result.data.markdown, domain);
      if (reviews.length > 0) {
        return groupReviewsByProduct(reviews);
      }
    }
  }

  // Strategy 3: Scrape the homepage and product pages for inline reviews
  const homepageResult = await firecrawlScrape(`https://${domain}`, env.FIRECRAWL_API_KEY, {
    formats: ['markdown'],
    waitFor: 5000,
  });

  if (homepageResult.success && homepageResult.data?.markdown) {
    const reviews = extractReviewsFromMarkdown(homepageResult.data.markdown, domain);
    if (reviews.length > 0) {
      return groupReviewsByProduct(reviews);
    }
  }

  return [];
}

export const judgemeExtractor: ReviewExtractor = {
  name: 'judgeme',
  detect(domain: string, pageContent: string): boolean {
    return JUDGEME_PATTERNS.some((p) => p.test(pageContent));
  },
  extract(domain: string, env: Env): Promise<ProductReviewSummary[]> {
    return extractJudgeMeReviews(domain, env);
  },
};
