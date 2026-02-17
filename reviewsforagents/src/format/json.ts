import type { ProductReviewSummary } from '../types';

export function formatAsJson(
  domain: string,
  summaries: ProductReviewSummary[],
  productHandle: string | null,
): string {
  const totalReviews = summaries.reduce((sum, s) => sum + s.totalReviews, 0);
  const weightedRating =
    totalReviews > 0
      ? summaries.reduce((sum, s) => sum + s.averageRating * s.totalReviews, 0) / totalReviews
      : 0;
  const avgVerified =
    totalReviews > 0
      ? summaries.reduce((sum, s) => sum + s.verifiedPercentage * s.totalReviews, 0) /
        totalReviews
      : 0;

  let target = summaries;
  if (productHandle) {
    const filtered = summaries.filter(
      (s) =>
        s.productHandle === productHandle ||
        s.productTitle.toLowerCase().includes(productHandle.replace(/-/g, ' ')),
    );
    if (filtered.length > 0) target = filtered;
  }

  const output = {
    domain,
    overallRating: Math.round(weightedRating * 10) / 10,
    totalReviews,
    verifiedPercentage: Math.round(avgVerified),
    products: target.map((s) => ({
      title: s.productTitle,
      handle: s.productHandle,
      rating: s.averageRating,
      reviewCount: s.totalReviews,
      verifiedPercentage: s.verifiedPercentage,
      ratingDistribution: s.ratingDistribution,
    })),
    specVersion: '0.1',
    generatedAt: new Date().toISOString(),
  };

  return JSON.stringify(output, null, 2);
}
