
The new version of Kreuzberg represents a massive architectural evolution. **Kreuzberg has been completely rewritten in Rust** - leveraging Rust''s memory safety, zero-cost abstractions, and native performance. The new architecture consists of a high-performance Rust core with native bindings to multiple languages. That''s right - it''s no longer just a Python library.

**Kreuzberg v4 is now available for 7 languages across 8 runtime bindings:**

- **Rust** (native library)
- **Python** (PyO3 native bindings)
- **TypeScript** - Node.js (NAPI-RS native bindings) + Deno/Browser/Edge (WASM)
- **Ruby** (Magnus FFI)
- **Java 25+** (Panama Foreign Function & Memory API)
- **C#** (P/Invoke)
- **Go** (cgo bindings)

**Post v4.0.0 roadmap includes:**

- PHP
- Elixir (via Rustler - with Erlang and Gleam interop)

Additionally, it''s available as a **CLI** (installable via `cargo` or `homebrew`), **HTTP REST API server**, **Model Context Protocol (MCP) server** for Claude Desktop/Continue.dev, and as **public Docker images**.

### Why the Rust Rewrite? Performance and Architecture

The Rust rewrite wasn''t just about performance - though that''s a major benefit. It was an opportunity to fundamentally rethink the architecture:

**Architectural improvements:**
- **Zero-copy operations** via Rust''s ownership model
- **True async concurrency** with Tokio runtime (no GIL limitations)
- **Streaming parsers** for constant memory usage on multi-GB files
- **SIMD-accelerated text processing** for token reduction and string operations
- **Memory-safe FFI boundaries** for all language bindings
- **Plugin system** with trait-based extensibility

### v3 vs v4: What Changed?

| Aspect | v3 (Python) | v4 (Rust Core) |
|--------|-------------|----------------|
| **Core Language** | Pure Python | Rust 2024 edition |
| **File Formats** | 30-40+ (via Pandoc) | **56+ (native parsers)** |
| **Language Support** | Python only | **7 languages** (Rust/Python/TS/Ruby/Java/Go/C#) |
| **Dependencies** | Requires Pandoc (system binary) | **Zero system dependencies** (all native) |
| **Embeddings** | Not supported | ✓ FastEmbed with ONNX (3 presets + custom) |
| **Semantic Chunking** | Via semantic-text-splitter library | ✓ Built-in (text + markdown-aware) |
| **Token Reduction** | Built-in (TF-IDF based) | ✓ Enhanced with 3 modes |
| **Language Detection** | Optional (fast-langdetect) | ✓ Built-in (68 languages) |
| **Keyword Extraction** | Optional (KeyBERT) | ✓ Built-in (YAKE + RAKE algorithms) |
| **OCR Backends** | Tesseract/EasyOCR/PaddleOCR | **Same + better integration** |
| **Plugin System** | Limited extractor registry | **Full trait-based** (4 plugin types) |
| **Page Tracking** | Character-based indices | **Byte-based with O(1) lookup** |
| **Servers** | REST API (Litestar) | **HTTP (Axum) + MCP + MCP-SSE** |
| **Installation Size** | ~100MB base | **16-31 MB complete** |
