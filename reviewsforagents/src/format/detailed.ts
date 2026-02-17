import type { ProductReviewSummary } from '../types';

// Fallback detailed formatter — deterministic, no API call needed.

export function formatDetailed(
  domain: string,
  summary: ProductReviewSummary,
): string {
  const lines: string[] = [];

  lines.push(
    `# ${summary.productTitle} — ${domain} | ${summary.averageRating}★ | ${formatCount(summary.totalReviews)} reviews`,
  );
  lines.push('');

  // Rating Distribution
  lines.push('## Rating Distribution');
  const maxCount = Math.max(...Object.values(summary.ratingDistribution));
  for (let star = 5; star >= 1; star--) {
    const count = summary.ratingDistribution[star] || 0;
    const pct =
      summary.totalReviews > 0 ? Math.round((count / summary.totalReviews) * 100) : 0;
    const barLen = maxCount > 0 ? Math.round((count / maxCount) * 16) : 0;
    const bar = '█'.repeat(barLen);
    lines.push(`${star}★ ${bar} ${pct}%`);
  }
  lines.push('');

  // Recent reviews
  if (summary.reviews.length > 0) {
    lines.push('## Recent Highlights');
    const recent = summary.reviews.slice(0, 5);
    for (const review of recent) {
      const v = review.verified ? 'verified' : 'unverified';
      const snippet =
        review.body.length > 80 ? review.body.slice(0, 80) + '…' : review.body;
      lines.push(`- ${review.rating}★ "${snippet}" — ${v}`);
    }
  }

  return lines.join('\n');
}

function formatCount(n: number): string {
  if (n >= 1000) return `${(n / 1000).toFixed(1)}K`;
  return n.toString();
}
