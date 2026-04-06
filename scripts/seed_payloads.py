"""Seed payload corpus from default bundles."""

from __future__ import annotations

from navil.mutator.corpus import PayloadCorpus


def main() -> None:
    corpus = PayloadCorpus()
    for category in ["xss", "sqli", "ssrf", "lfi", "rce"]:
        payloads = corpus.load(category)
        print(f"{category}: {len(payloads)} payloads available")


if __name__ == "__main__":
    main()
