import type { Env, OutputFormat } from './types';
import { parseRequest, notFoundResponse, errorResponse } from './router';
import { cacheKey, getCached, setCache } from './cache';
import { detectReviewSource } from './detect/index';
import { extractReviews } from './extract/index';
import { compressReviews } from './compress/index';

// Simple in-memory rate limiting (resets per-isolate)
const rateLimiter = new Map<string, { count: number; resetAt: number }>();
const RATE_LIMIT = 100; // requests per hour per IP
const RATE_WINDOW = 3600000; // 1 hour in ms

function checkRateLimit(ip: string): boolean {
  const now = Date.now();
  const entry = rateLimiter.get(ip);

  if (!entry || now > entry.resetAt) {
    rateLimiter.set(ip, { count: 1, resetAt: now + RATE_WINDOW });
    return true;
  }

  entry.count++;
  return entry.count <= RATE_LIMIT;
}

function contentType(format: OutputFormat): string {
  return format === 'json' ? 'application/json; charset=utf-8' : 'text/markdown; charset=utf-8';
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    // Only allow GET requests
    if (request.method !== 'GET') {
      return errorResponse('Method not allowed. Use GET.', 405);
    }

    // Rate limiting
    const ip = request.headers.get('cf-connecting-ip') || 'unknown';
    if (!checkRateLimit(ip)) {
      return errorResponse('Rate limit exceeded. Max 100 requests/hour.', 429);
    }

    // Parse the request
    const parsed = parseRequest(request);
    if (!parsed) {
      return notFoundResponse();
    }

    const { domain, productHandle, format } = parsed;

    try {
      // 1. Check cache
      const key = cacheKey(domain, productHandle, format);
      const cached = await getCached(key, env);
      if (cached) {
        return new Response(cached, {
          headers: {
            'Content-Type': contentType(format),
            'X-Cache': 'HIT',
            'X-Spec-Version': '0.1',
            'Access-Control-Allow-Origin': '*',
          },
        });
      }

      // 2. Detect review source
      const detection = await detectReviewSource(domain, env);

      // If we can't detect a supported review app, return early
      if (detection.reviewApp === 'unknown') {
        const fallback = `# ${domain} | Review source not yet supported\n\nDetected platform: ${detection.platform}\nSupported review apps: Judge.me\n\nTry: trustpilot.com/review/${domain}`;
        // Cache the miss for 1 hour to avoid repeated scraping
        await setCache(key, fallback, env, 3600);
        return new Response(fallback, {
          headers: {
            'Content-Type': 'text/markdown; charset=utf-8',
            'X-Cache': 'MISS',
            'X-Source': 'none',
            'X-Spec-Version': '0.1',
            'Access-Control-Allow-Origin': '*',
          },
        });
      }

      // 3. Extract reviews
      const reviews = await extractReviews(domain, detection, env);

      // 4. Compress to target format
      const markdown = await compressReviews(domain, reviews, format, productHandle, env);

      // 5. Cache and return
      await setCache(key, markdown, env);

      const totalReviews = reviews.reduce((sum, p) => sum + p.totalReviews, 0);

      return new Response(markdown, {
        headers: {
          'Content-Type': contentType(format),
          'X-Cache': 'MISS',
          'X-Source': detection.reviewApp,
          'X-Reviews-Count': totalReviews.toString(),
          'X-Spec-Version': '0.1',
          'X-Generated': new Date().toISOString(),
          'Access-Control-Allow-Origin': '*',
        },
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error';
      console.error(`Error processing ${domain}:`, message);
      return errorResponse(`Failed to process reviews for ${domain}.\n\n${message}`, 502);
    }
  },
};
