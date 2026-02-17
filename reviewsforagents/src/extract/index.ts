import type { DetectionResult, Env, ProductReviewSummary } from '../types';
import { extractJudgeMeReviews } from './judgeme';

export async function extractReviews(
  domain: string,
  detection: DetectionResult,
  env: Env,
): Promise<ProductReviewSummary[]> {
  switch (detection.reviewApp) {
    case 'judgeme':
      return extractJudgeMeReviews(domain, env);

    // Phase 2 extractors:
    // case 'yotpo': return extractYotpoReviews(domain, env);
    // case 'stamped': return extractStampedReviews(domain, env);
    // case 'loox': return extractLooxReviews(domain, env);
    // case 'okendo': return extractOkendoReviews(domain, env);

    default:
      return [];
  }
}
