import type { DetectionResult, Env, ReviewApp } from '../types';
import { firecrawlScrape } from '../extract/firecrawl';

const REVIEW_APP_SIGNALS: Record<ReviewApp, RegExp[]> = {
  judgeme: [
    /judge\.me/i,
    /judgeme/i,
    /jdgm-widget/i,
    /jdgm-rev/i,
    /jdgm-preview-badge/i,
    /data-jdgm/i,
  ],
  yotpo: [
    /yotpo\.com/i,
    /yotpo-widget/i,
    /yotpo-main-widget/i,
    /yotpo-reviews/i,
    /data-yotpo/i,
  ],
  stamped: [
    /stamped\.io/i,
    /stamped-main-widget/i,
    /stamped-reviews/i,
    /data-stamped/i,
  ],
  loox: [
    /loox\.io/i,
    /loox-rating/i,
    /loox-reviews/i,
    /data-loox/i,
  ],
  okendo: [
    /okendo/i,
    /oke-widget/i,
    /oke-reviews/i,
    /data-oke/i,
  ],
  unknown: [],
};

function isShopifyStore(html: string): boolean {
  const shopifySignals = [
    /Shopify\.shop/i,
    /cdn\.shopify\.com/i,
    /shopify-section/i,
    /myshopify\.com/i,
    /shopify\.com\/s\//i,
    /Shopify\.theme/i,
  ];
  return shopifySignals.some((pattern) => pattern.test(html));
}

function detectReviewAppFromHtml(html: string): { app: ReviewApp; confidence: number; signals: string[] } {
  let bestApp: ReviewApp = 'unknown';
  let bestScore = 0;
  let bestSignals: string[] = [];

  for (const [app, patterns] of Object.entries(REVIEW_APP_SIGNALS)) {
    if (app === 'unknown') continue;
    const matched = patterns.filter((p) => p.test(html));
    if (matched.length > bestScore) {
      bestScore = matched.length;
      bestApp = app as ReviewApp;
      bestSignals = matched.map((p) => p.source);
    }
  }

  const confidence = bestScore === 0 ? 0 : Math.min(bestScore / 3, 1);
  return { app: bestApp, confidence, signals: bestSignals };
}

export async function detectShopifyReviewApp(
  domain: string,
  env: Env,
): Promise<DetectionResult> {
  const url = `https://${domain}`;

  const result = await firecrawlScrape(url, env.FIRECRAWL_API_KEY, { formats: ['html'] });

  if (!result.success || !result.data?.html) {
    return {
      platform: 'unknown',
      reviewApp: 'unknown',
      confidence: 0,
      signals: ['scrape_failed'],
    };
  }

  const html = result.data.html;
  const shopify = isShopifyStore(html);
  const { app, confidence, signals } = detectReviewAppFromHtml(html);

  return {
    platform: shopify ? 'shopify' : 'unknown',
    reviewApp: app,
    confidence,
    signals,
  };
}
