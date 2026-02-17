import type { Env, OutputFormat, ProductReviewSummary } from '../types';
import { compressWithClaude } from './ecom';
import { formatAsJson } from '../format/json';

export async function compressReviews(
  domain: string,
  summaries: ProductReviewSummary[],
  format: OutputFormat,
  productHandle: string | null,
  env: Env,
): Promise<string> {
  // JSON format doesn't need Claude compression — return structured data directly
  if (format === 'json') {
    return formatAsJson(domain, summaries, productHandle);
  }

  // If no reviews found, return a minimal response
  if (summaries.length === 0) {
    return noReviewsResponse(domain);
  }

  // If requesting a specific product in detailed mode, filter to that product
  let targetSummaries = summaries;
  if (productHandle) {
    const filtered = summaries.filter(
      (s) =>
        s.productHandle === productHandle ||
        s.productHandle === productHandle.toLowerCase() ||
        s.productTitle.toLowerCase().includes(productHandle.replace(/-/g, ' ')),
    );
    if (filtered.length > 0) {
      targetSummaries = filtered;
    }
  }

  return compressWithClaude(domain, targetSummaries, format, productHandle, env.ANTHROPIC_API_KEY);
}

function noReviewsResponse(domain: string): string {
  return `# ${domain} | No structured reviews found

No review data could be extracted for this domain.
Possible reasons:
- Review app not yet supported (currently supporting: Judge.me)
- No reviews present on the store
- Store is not publicly accessible

Try: trustpilot.com/review/${domain}`;
}
