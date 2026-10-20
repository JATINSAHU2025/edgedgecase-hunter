"""Build MobileCLIP2-S2 embeddings for a hardware product image catalog."""
import argparse
from mobileclip2_provider import build_catalog_index

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", default="catalog/products.csv", help="Product CSV path")
    parser.add_argument("--root", default="catalog", help="Root directory containing image_path values")
    parser.add_argument("--output", default="catalog/catalog_embeddings.pt", help="Output index path")
    args = parser.parse_args()
    count = build_catalog_index(args.csv, args.output, args.root)
    print(f"Indexed {count} product reference images into {args.output}")

if __name__ == "__main__":
    main()
