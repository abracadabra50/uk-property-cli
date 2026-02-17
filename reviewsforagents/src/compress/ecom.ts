import type { ProductReviewSummary, OutputFormat } from '../types';
import {
  SYSTEM_PROMPT,
  standardFormatPrompt,
  minifiedFormatPrompt,
  detailedFormatPrompt,
} from './prompts';

function serializeReviewData(summaries: ProductReviewSummary[]): string {
  const lines: string[] = [];

  for (const product of summaries) {
    lines.push(`## ${product.productTitle} (${product.productHandle})`);
    lines.push(`Rating: ${product.averageRating}/5 (${product.totalReviews} reviews, ${product.verifiedPercentage}% verified)`);
    lines.push(
      `Distribution: 5★=${product.ratingDistribution[5] || 0} 4★=${product.ratingDistribution[4] || 0} 3★=${product.ratingDistribution[3] || 0} 2★=${product.ratingDistribution[2] || 0} 1★=${product.ratingDistribution[1] || 0}`,
    );

    // Include up to 20 reviews per product to keep Claude's input manageable
    const reviewSubset = product.reviews.slice(0, 20);
    for (const review of reviewSubset) {
      const verified = review.verified ? '[V]' : '';
      lines.push(`- ${review.rating}★ ${verified} "${review.title}" — ${review.body.slice(0, 300)}`);
    }
    lines.push('');
  }

  return lines.join('\n');
}

export async function compressWithClaude(
  domain: string,
  summaries: ProductReviewSummary[],
  format: OutputFormat,
  productHandle: string | null,
  apiKey: string,
): Promise<string> {
  const serialized = serializeReviewData(summaries);

  let userPrompt: string;
  switch (format) {
    case 'min':
      userPrompt = minifiedFormatPrompt(domain, serialized);
      break;
    case 'detailed':
      userPrompt = detailedFormatPrompt(domain, productHandle || '', serialized);
      break;
    case 'standard':
    default:
      userPrompt = standardFormatPrompt(domain, serialized);
      break;
  }

  const response = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': apiKey,
      'anthropic-version': '2023-06-01',
    },
    body: JSON.stringify({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 1024,
      system: SYSTEM_PROMPT,
      messages: [{ role: 'user', content: userPrompt }],
    }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Anthropic API error: ${response.status} — ${errorText}`);
  }

  const data = (await response.json()) as {
    content: Array<{ type: string; text?: string }>;
  };

  const textBlock = data.content.find((b) => b.type === 'text');
  return textBlock?.text || '';
}
