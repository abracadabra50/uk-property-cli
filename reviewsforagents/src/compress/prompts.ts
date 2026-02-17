export const SYSTEM_PROMPT = `You are a review data compression engine. Your audience is AI agents making purchase recommendations, NOT humans.

Rules:
- Be ruthlessly concise. Every token must carry signal.
- Use sentiment tags with + for positive and - for negative themes.
- Normalize ratings to a 5-point scale.
- Prefer concrete data (numbers, percentages) over vague language.
- Never include marketing language or brand-speak.
- Never include disclaimers or caveats about your analysis.
- Output ONLY the requested format, no explanations.`;

export function standardFormatPrompt(domain: string, reviewData: string): string {
  return `Compress the following review data for "${domain}" into this exact format:

# {domain} | {overall_rating}★ | {total_count} reviews | {verified_pct}% verified

## Top Products
{product} | {rating}★ ({count}) | {one-line summary of key themes}
[repeat for top 5-10 products by review count]

## Sentiment
+{positive_theme} +{positive_theme} +{positive_theme}
-{negative_theme} -{negative_theme}

## Trust
Response rate: {pct}% | Avg response: {time} | Return mentions: {pct}%

If data for Trust fields is not available, omit the Trust section entirely.
If there are fewer than 3 products, show all of them.
Product one-line summaries should capture the 2-3 most mentioned themes, both positive and negative.

Review data:
${reviewData}`;
}

export function minifiedFormatPrompt(domain: string, reviewData: string): string {
  return `Compress the following review data for "${domain}" into this minified format:

{domain};{overall_rating};{total_count};{verified_pct}%v|{product_handle}:{rating}:{count}:+{pos}-{neg}|{product_handle}:{rating}:{count}:+{pos}-{neg}

Rules:
- Use semicolons between domain-level fields
- Use pipes between products
- Use colons between product-level fields
- Sentiment tags are concatenated with no spaces: +comfort+lightweight-durability
- Include top 5 products max
- No spaces, no newlines, just the single line

Review data:
${reviewData}`;
}

export function detailedFormatPrompt(
  domain: string,
  productHandle: string,
  reviewData: string,
): string {
  return `Compress the following review data for product "${productHandle}" from "${domain}" into this exact format:

# {Product Title} — {domain} | {rating}★ | {total_count} reviews

## Rating Distribution
5★ {bar} {pct}%
4★ {bar} {pct}%
3★ {bar} {pct}%
2★ {bar} {pct}%
1★ {bar} {pct}%

For the bar, use █ characters. Scale so the highest percentage gets 16 █ characters, and others are proportional.

## Key Themes
+{theme} (mentioned {count}x) | +{theme} ({count}x)
-{theme} ({count}x) | -{theme} ({count}x)

Include top 5 positive and top 3 negative themes.

## Recent Highlights (last 30 days)
- {rating}★ "{short quote}" — {verified/unverified}
[3-5 representative recent reviews]

Pick reviews that represent the range of experiences. Include at least one critical review if any exist.

## Fit Guide (from reviews)
True to size: {pct}% | Runs small: {pct}% | Runs large: {pct}%
Wide foot friendly: {assessment}

If fit data is not relevant or not available for this product type, omit the Fit Guide section.

Review data:
${reviewData}`;
}
