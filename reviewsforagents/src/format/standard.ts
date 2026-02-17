import type { ProductReviewSummary } from '../types';

// Fallback standard formatter when Claude API is unavailable.
// Normally the Claude API produces the standard format, but this serves as a
// deterministic backup that doesn't require an API call.

export function formatStandard(
  domain: string,
  summaries: ProductReviewSummary[],
): string {
  if (summaries.length === 0) {
    return `# ${domain} | No reviews found`;
  }

  const totalReviews = summaries.reduce((sum, s) => sum + s.totalReviews, 0);
  const weightedRating =
    summaries.reduce((sum, s) => sum + s.averageRating * s.totalReviews, 0) / totalReviews;
  const avgVerified =
    summaries.reduce((sum, s) => sum + s.verifiedPercentage * s.totalReviews, 0) / totalReviews;

  const lines: string[] = [];

  // Header
  lines.push(
    `# ${domain} | ${weightedRating.toFixed(1)}★ | ${formatCount(totalReviews)} reviews | ${Math.round(avgVerified)}% verified`,
  );
  lines.push('');

  // Top Products
  lines.push('## Top Products');
  const topProducts = summaries.slice(0, 10);
  for (const product of topProducts) {
    lines.push(
      `${product.productTitle} | ${product.averageRating}★ (${formatCount(product.totalReviews)})`,
    );
  }

  return lines.join('\n');
}

function formatCount(n: number): string {
  if (n >= 1000) return `${(n / 1000).toFixed(1)}K`;
  return n.toString();
}
