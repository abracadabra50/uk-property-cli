import type { ProductReviewSummary } from '../types';

// Fallback minified formatter — deterministic, no API call needed.

export function formatMinified(
  domain: string,
  summaries: ProductReviewSummary[],
): string {
  if (summaries.length === 0) {
    return `${domain};0;0;0%v`;
  }

  const totalReviews = summaries.reduce((sum, s) => sum + s.totalReviews, 0);
  const weightedRating =
    summaries.reduce((sum, s) => sum + s.averageRating * s.totalReviews, 0) / totalReviews;
  const avgVerified =
    summaries.reduce((sum, s) => sum + s.verifiedPercentage * s.totalReviews, 0) / totalReviews;

  const header = `${domain};${weightedRating.toFixed(1)};${totalReviews};${Math.round(avgVerified)}%v`;

  const productParts = summaries.slice(0, 5).map((s) => {
    return `${s.productHandle}:${s.averageRating}:${s.totalReviews}`;
  });

  return [header, ...productParts].join('|');
}
