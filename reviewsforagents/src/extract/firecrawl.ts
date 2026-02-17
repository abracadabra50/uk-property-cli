import type { FirecrawlScrapeResult } from '../types';

interface ScrapeOptions {
  formats?: ('markdown' | 'html')[];
  waitFor?: number;
}

export async function firecrawlScrape(
  url: string,
  apiKey: string,
  options: ScrapeOptions = {},
): Promise<FirecrawlScrapeResult> {
  const { formats = ['markdown'], waitFor = 3000 } = options;

  const response = await fetch('https://api.firecrawl.dev/v1/scrape', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify({
      url,
      formats,
      waitFor,
    }),
  });

  if (!response.ok) {
    return {
      success: false,
      error: `Firecrawl API error: ${response.status} ${response.statusText}`,
    };
  }

  const body = (await response.json()) as FirecrawlScrapeResult;
  return body;
}

export async function firecrawlScrapeMultiple(
  urls: string[],
  apiKey: string,
  options: ScrapeOptions = {},
): Promise<FirecrawlScrapeResult[]> {
  return Promise.all(urls.map((url) => firecrawlScrape(url, apiKey, options)));
}
