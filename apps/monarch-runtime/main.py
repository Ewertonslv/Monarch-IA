"""Wrapper canonico do runtime principal do Monarch."""

import asyncio

from main import main as monarch_main


if __name__ == "__main__":
    asyncio.run(monarch_main())
