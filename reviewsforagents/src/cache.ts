import type { Env, OutputFormat } from './types';

const DEFAULT_TTL = 21600; // 6 hours in seconds

export function cacheKey(
  domain: string,
  productHandle: string | null,
  format: OutputFormat,
): string {
  const product = productHandle || 'all';
  return `v1:${domain}:${product}:${format}`;
}

export async function getCached(
  key: string,
  env: Env,
): Promise<string | null> {
  return env.REVIEW_CACHE.get(key);
}

export async function setCache(
  key: string,
  value: string,
  env: Env,
  ttl: number = DEFAULT_TTL,
): Promise<void> {
  await env.REVIEW_CACHE.put(key, value, { expirationTtl: ttl });
}
