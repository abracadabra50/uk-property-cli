import type { OutputFormat, ParsedRequest } from './types';

const VALID_FORMATS = new Set<OutputFormat>(['standard', 'min', 'detailed', 'json']);

export function parseRequest(request: Request): ParsedRequest | null {
  const url = new URL(request.url);
  const path = url.pathname.slice(1); // remove leading /

  if (!path || path === 'favicon.ico' || path === 'robots.txt') {
    return null;
  }

  // Split: first segment is domain, optional second is product handle
  const parts = path.split('/').filter(Boolean);
  const domain = parts[0];
  const productHandle = parts[1] || null;

  // Validate domain looks reasonable
  if (!domain.includes('.') || domain.length < 4) {
    return null;
  }

  // Parse format query param
  const formatParam = url.searchParams.get('format') || 'standard';
  const format: OutputFormat = VALID_FORMATS.has(formatParam as OutputFormat)
    ? (formatParam as OutputFormat)
    : 'standard';

  // If a product handle is specified, default to detailed format
  const effectiveFormat = productHandle && formatParam === 'standard' ? 'detailed' : format;

  return {
    domain: domain.toLowerCase(),
    productHandle,
    format: effectiveFormat,
  };
}

export function notFoundResponse(): Response {
  return new Response(
    '# reviewsforagents.md\n\nUsage: GET /{domain} — e.g., /allbirds.com\n\nOptions:\n- /{domain}?format=min — minified output\n- /{domain}?format=json — JSON output\n- /{domain}/{product-handle} — detailed product view\n',
    {
      status: 200,
      headers: { 'Content-Type': 'text/markdown; charset=utf-8' },
    },
  );
}

export function errorResponse(message: string, status: number = 500): Response {
  return new Response(`# Error\n\n${message}`, {
    status,
    headers: { 'Content-Type': 'text/markdown; charset=utf-8' },
  });
}
