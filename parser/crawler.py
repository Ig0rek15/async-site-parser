import asyncio
import json
import logging
import os
import sys

from typing import Set
from urllib.parse import urlparse, urljoin

import aiohttp
from bs4 import BeautifulSoup

from .extractors import extract_emails, extract_phones
from .constants import (
    DEFAULT_CONCURRENCY,
    DEFAULT_MAX_PAGES,
    REQUEST_TIMEOUT,
    HTTP_OK,
)

logger = logging.getLogger(__name__)


async def parse_site(
    start_url: str,
    max_pages: int = DEFAULT_MAX_PAGES,
    concurrency: int = DEFAULT_CONCURRENCY,
) -> dict:
    parsed_start = urlparse(start_url)
    base_domain = parsed_start.netloc

    visited: Set[str] = set()
    emails: Set[str] = set()
    phones: Set[str] = set()

    queue: asyncio.Queue[str] = asyncio.Queue()
    await queue.put(start_url)

    timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        semaphore = asyncio.Semaphore(concurrency)

        workers = [
            asyncio.create_task(
                _worker(
                    session=session,
                    queue=queue,
                    visited=visited,
                    emails=emails,
                    phones=phones,
                    base_domain=base_domain,
                    max_pages=max_pages,
                    semaphore=semaphore,
                )
            )
            for _ in range(concurrency)
        ]

        await queue.join()

        for worker in workers:
            worker.cancel()

    result = {
        'url': start_url,
        'emails': sorted(emails),
        'phones': sorted(phones),
    }

    print(json.dumps(result, indent=2, ensure_ascii=False))

    os.makedirs('results', exist_ok=True)
    domain = base_domain.replace(':', '_')

    with open(f'results/{domain}.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    return result


async def _fetch(
    session: aiohttp.ClientSession,
    url: str,
    semaphore: asyncio.Semaphore,
) -> str | None:
    async with semaphore:
        try:
            async with session.get(url) as response:
                if response.status != HTTP_OK:
                    logger.warning(
                        f'Non-200 response {response.status} for {url}'
                    )
                    return None

                return await response.text(errors='ignore')

        except asyncio.TimeoutError:
            logger.warning(f'Timeout while fetching {url}')
        except aiohttp.ClientError as exc:
            logger.warning(f'HTTP error for {url}: {exc}')

    return None


async def _worker(
    session: aiohttp.ClientSession,
    queue: asyncio.Queue[str],
    visited: Set[str],
    emails: Set[str],
    phones: Set[str],
    base_domain: str,
    max_pages: int,
    semaphore: asyncio.Semaphore,
) -> None:
    while True:
        url = await queue.get()
        try:
            if len(visited) >= max_pages:
                continue

            if url in visited:
                continue

            visited.add(url)

            html = await _fetch(session, url, semaphore)
            if not html:
                continue

            soup = BeautifulSoup(html, 'html.parser')
            text = soup.get_text(' ', strip=True)

            emails.update(extract_emails(text))
            phones.update(extract_phones(text))

            for tag in soup.find_all('a', href=True):
                absolute_url = urljoin(url, tag['href'])
                parsed = urlparse(absolute_url)

                if parsed.netloc != base_domain:
                    continue

                if absolute_url not in visited:
                    await queue.put(absolute_url)

        finally:
            queue.task_done()


def main() -> None:
    if len(sys.argv) < 2:
        print('Usage: python -m parser.crawler <start_url>')
        sys.exit(1)

    start_url = sys.argv[1]

    asyncio.run(parse_site(start_url))


if __name__ == '__main__':
    main()
