import type { DetectionResult, Env } from '../types';
import { detectShopifyReviewApp } from './shopify';

export async function detectReviewSource(
  domain: string,
  env: Env,
): Promise<DetectionResult> {
  // Phase 1: Try Shopify detection
  const result = await detectShopifyReviewApp(domain, env);

  // If we found a review app with any confidence, return it
  if (result.reviewApp !== 'unknown' && result.confidence > 0) {
    return result;
  }

  // If it's a Shopify store but we couldn't detect the review app
  if (result.platform === 'shopify') {
    return {
      ...result,
      reviewApp: 'unknown',
      signals: [...result.signals, 'shopify_store_detected_but_no_review_app'],
    };
  }

  // Phase 2+: Add Trustpilot fallback, restaurant detection, etc.
  return {
    platform: 'unknown',
    reviewApp: 'unknown',
    confidence: 0,
    signals: ['no_review_source_detected'],
  };
}
