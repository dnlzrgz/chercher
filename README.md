# 🔍 Chercher - My Universal Search Engine

**Chercher** is my personal search engine for everything. It chews through PDFs, ebooks, YouTube videos, RSS feeds, and my own notes to help me rediscover anything I've seen, read, or written. Built on top of SQLite, it's designed to be fast enough for daily use and simple enough that I can extend it whenever I need to.

## Features

- **Pluggable architecture** that adapts to your needs:  
  - Official plugins for [PDFs](https://github.com/dnlzrgz/chercher-plugin-pdf), [EPUBs](https://github.com/dnlzrgz/chercher-plugin-epub), [YouTube videos](https://github.com/dnlzrgz/chercher-plugin-yt) and [more](https://pypi.org/search/?q=chercher-plugin)
- **Building your own plugins is minutes**:
  - Starter template with [Cookiecutter](https://github.com/dnlzrgz/chercher-plugin)
  - Simple Python interface (just implemented the methods you want.)

- **BM25-powered search at SQLite speed**:
  - Industry-standard ranking algorithm
  - Supports advanced query operators
- **Progressive indexing**:
  - Files become searchable immediately
  - No full-rebuilds required
  - Stop and resume anytime
  - Handles incremental updates gracefully
- **Terminal-native workflow**:
  - Easy-to-use CLI with intuitive commands
  - Structured output for quick scanning
  - Pipe-friendly for power users (WIP)
- **And more coming soon**:
  - Modern TUI (WIP)
  - Auto-suggestion engine (WIP)
  - Granular search filters (WIP)
  - Hook for incremental updates (WIP)

## Motivation

Building my own personal search engine has been a recurring project that never quite stuck. My first attempt, [winzig](https://github.com/dnlzrgz/winzing), taught me about the basics but felt too rigid. Then [housaku](https://github.com/dnlzrgz/housaku) became an over-engineered lesson in scope creep. But with each iteration, I learned what really matters for me and a great deal about search engines in general.

Chercher is the distillation of those lessons.

## Installion

> [!NOTE]
> TODO

## Usage

> [!NOTE]
> TODO
