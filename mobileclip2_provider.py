"""MobileCLIP2-S2 zero-shot hardware recognizer for EdgeCase Hunter AI.

The checkpoint is downloaded from Apple's official Hugging Face repository on first use.
This provider ranks a curated hardware vocabulary. It is not SKU-level catalog retrieval;
for exact variants, add catalog-image embeddings and metadata in a later stage.
"""
from __future__ import annotations

import csv
import io
import json
import os
import threading
from pathlib import Path

# Curated labels for the hardware-shop use case. Keep labels specific but visually observable.
HARDWARE_LABELS = [
    "ceramic wash basin", "pedestal wash basin", "wall-mounted wash basin", "western toilet commode",
    "Indian squat toilet pan", "urinal", "toilet seat cover", "toilet flush tank", "health faucet spray",
    "shower head", "bathroom mixer tap", "pillar tap", "bib tap", "angle valve", "brass ball valve",
    "gate valve", "check valve", "PVC water pipe", "CPVC water pipe", "UPVC drainage pipe",
    "PVC pipe elbow fitting", "PVC pipe tee fitting", "PVC pipe socket coupling", "pipe reducer fitting",
    "pipe union fitting", "brass pipe nipple", "threaded pipe connector", "flexible water hose",
    "floor drain grate", "kitchen sink", "stainless steel sink", "sink mixer tap", "water tank",
    "water pump", "water filter housing", "PVC electrical conduit", "electrical junction box",
    "electrical switch", "electrical socket outlet", "modular switch plate", "MCB circuit breaker",
    "RCCB circuit breaker", "electrical distribution board", "electrical wire coil", "copper electrical cable",
    "LED bulb", "LED tube light", "ceiling light fixture", "ceiling fan", "exhaust fan", "plug top",
    "extension power strip", "electrical connector terminal", "cable tie", "insulation tape",
    "wire stripper tool", "combination pliers", "long nose pliers", "adjustable spanner wrench",
    "open-end spanner", "screwdriver", "hammer", "claw hammer", "measuring tape", "spirit level",
    "hand saw", "hacksaw", "drill machine", "angle grinder", "cutting disc", "drill bit",
    "screw fastener", "wall plug anchor", "hex bolt", "nut and washer", "hinge", "door handle",
    "door lock", "padlock", "cabinet knob", "drawer slide rail", "silicone sealant tube",
    "construction adhesive tube", "PVC solvent cement can", "tile adhesive bag", "grout bag",
    "paint brush", "paint roller", "paint can", "putty knife", "trowel", "plumbing wrench",
    "pipe wrench", "hose clamp", "rubber gasket", "O-ring seal", "PTFE thread seal tape",
    "waterproofing chemical container", "PU foam spray can", "metal bracket", "steel angle bracket",
    "stainless steel screw", "brass fitting", "plastic plumbing fitting", "ceramic tile", "tile spacer",
    "building material bag", "hardware product package", "barcode label on a product", "other household or hardware object"
]

_PROMPT_TEMPLATES = (
    "a clear product photo of {label}",
    "a close-up photo of {label} sold in a hardware store",
    "a single {label} on a plain background",
)

_lock = threading.Lock()
_state: dict | None = None
_catalog_state: dict | None = None
_catalog_lock = threading.Lock()


def _load_model() -> dict:
    global _state
    if _state is not None:
        return _state
    with _lock:
        if _state is not None:
            return _state
        try:
            import torch
            import open_clip
            from huggingface_hub import hf_hub_download
            from PIL import Image
            from mobileclip.modules.common.mobileone import reparameterize_model
        except Exception as exc:
            raise RuntimeError(
                "MobileCLIP2 runtime is missing. Build the backend with its MobileCLIP2 Dockerfile dependencies."
            ) from exc

        checkpoint = os.getenv("MOBILECLIP2_CHECKPOINT", "").strip()
        if not checkpoint:
            checkpoint = hf_hub_download(
                repo_id="apple/MobileCLIP2-S2",
                filename="mobileclip2_s2.pt",
            )

        # This model variant uses zero/one image normalization in Apple's published example.
        model, _, preprocess = open_clip.create_model_and_transforms(
            "MobileCLIP2-S2",
            pretrained=checkpoint,
            image_mean=(0.0, 0.0, 0.0),
            image_std=(1.0, 1.0, 1.0),
        )
        model.eval()
        model = reparameterize_model(model)
        model.to("cpu")
        tokenizer = open_clip.get_tokenizer("MobileCLIP2-S2")

        prompt_texts = [template.format(label=label) for label in HARDWARE_LABELS for template in _PROMPT_TEMPLATES]
        tokens = tokenizer(prompt_texts)
        with torch.inference_mode():
            text_features = model.encode_text(tokens)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True).clamp_min(1e-12)
            text_features = text_features.reshape(len(HARDWARE_LABELS), len(_PROMPT_TEMPLATES), -1).mean(dim=1)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True).clamp_min(1e-12)

        _state = {
            "torch": torch,
            "Image": Image,
            "model": model,
            "preprocess": preprocess,
            "text_features": text_features,
            "device": "cpu",
        }
        return _state


def _load_catalog_index(state: dict) -> dict | None:
    """Load precomputed catalog embeddings once. Missing index is a supported mode."""
    global _catalog_state
    if _catalog_state is not None:
        return _catalog_state
    with _catalog_lock:
        if _catalog_state is not None:
            return _catalog_state
        index_path = Path(os.getenv("CATALOG_EMBEDDINGS_PATH", "catalog/catalog_embeddings.pt"))
        if not index_path.is_file():
            _catalog_state = None
            return None
        try:
            # This is an application-generated local artifact, not user-uploaded input.
            payload = state["torch"].load(str(index_path), map_location="cpu", weights_only=False)
            if payload.get("model") != "MobileCLIP2-S2":
                raise ValueError("Catalog embeddings were created with a different model.")
            embeddings = payload.get("embeddings")
            products = payload.get("products")
            if embeddings is None or not products or len(products) != len(embeddings):
                raise ValueError("Catalog index is empty or malformed.")
            embeddings = embeddings.float()
            embeddings = embeddings / embeddings.norm(dim=-1, keepdim=True).clamp_min(1e-12)
            _catalog_state = {"embeddings": embeddings, "products": products}
        except Exception as exc:
            raise RuntimeError(f"Could not load catalog index at {index_path}: {exc}") from exc
        return _catalog_state


def _catalog_matches(image_features, state: dict, limit: int = 5) -> list[dict]:
    index = _load_catalog_index(state)
    if index is None:
        return []
    torch = state["torch"]
    similarities = (image_features @ index["embeddings"].T).squeeze(0)
    # Multiple views may exist for one SKU. Keep only the strongest image per product.
    order = similarities.argsort(descending=True).tolist()
    matches = []
    seen_products: set[str] = set()
    for idx in order:
        product = index["products"][int(idx)]
        product_id = str(product.get("product_id", "")).strip()
        # Prefer product_id, then SKU, then the unique row index to avoid accidental merges.
        dedupe_key = product_id or str(product.get("sku", "")).strip() or f"row-{idx}"
        if dedupe_key in seen_products:
            continue
        seen_products.add(dedupe_key)
        matches.append({
            "productId": product_id,
            "sku": str(product.get("sku", "")),
            "name": str(product.get("name", "Unknown product")),
            "category": str(product.get("category", "")),
            "brand": str(product.get("brand", "")),
            "dimensions": str(product.get("dimensions", "")),
            "price": str(product.get("price", "")),
            # Cosine similarity is a ranking score, not a probability.
            "similarity": round(float(similarities[int(idx)]), 4),
        })
        if len(matches) >= limit:
            break
    return matches


def classify_image(image_bytes: bytes) -> dict:
    """Return a ranked hardware category and optional exact-catalog candidates."""
    state = _load_model()
    torch = state["torch"]
    Image = state["Image"]
    try:
        with Image.open(io.BytesIO(image_bytes)) as source:
            image = source.convert("RGB")
            tensor = state["preprocess"](image).unsqueeze(0)
    except Exception as exc:
        raise ValueError("The uploaded image could not be decoded.") from exc

    with torch.inference_mode():
        image_features = state["model"].encode_image(tensor)
        image_features = image_features / image_features.norm(dim=-1, keepdim=True).clamp_min(1e-12)
        similarities = (image_features @ state["text_features"].T).squeeze(0)
        top_scores, top_indices = similarities.topk(k=5)

    indices = [int(i) for i in top_indices.tolist()]
    scores = [float(s) for s in top_scores.tolist()]
    category_name = HARDWARE_LABELS[indices[0]]
    category_margin = scores[0] - scores[1] if len(scores) > 1 else 0.0
    category_uncertainty = "low" if category_margin >= 0.08 else "medium" if category_margin >= 0.035 else "high"
    catalog_matches = _catalog_matches(image_features, state, limit=5)

    # Never silently claim an exact SKU from a weak visual match. Threshold must be calibrated
    # against the owner's own held-out catalog photos before production use.
    minimum_similarity = float(os.getenv("CATALOG_MIN_SIMILARITY", "0.20"))
    catalog_best = catalog_matches[0] if catalog_matches else None
    catalog_accepted = bool(catalog_best and float(catalog_best["similarity"]) >= minimum_similarity)
    name = catalog_best["name"] if catalog_accepted else category_name
    if catalog_accepted:
        uncertainty = "medium" if float(catalog_best["similarity"]) < minimum_similarity + 0.10 else "low"
        description = (
            "Closest visual match in your product catalog. Similarity is a ranking score, not a probability; "
            "verify SKU, dimensions, packaging, and price before billing."
        )
    else:
        uncertainty = category_uncertainty
        description = (
            "Best match from MobileCLIP2-S2's hardware-category vocabulary. "
            "No catalog match passed the configured threshold; confirm the category and check printed size, brand, and SKU."
            if catalog_matches else
            "Best match from MobileCLIP2-S2's hardware-category vocabulary. Add a catalog image index for product-specific matching. "
            "Confirm the product and check its printed size, brand, and SKU before billing."
        )

    alternatives = [HARDWARE_LABELS[i] for i in indices[1:] if HARDWARE_LABELS[i].lower() != category_name.lower()]
    if catalog_accepted:
        alternatives = [m["name"] for m in catalog_matches[1:5] if m["name"].lower() != name.lower()]
    return {
        "name": name,
        "description": description,
        "visibleFeatures": [],
        "alternatives": alternatives[:4],
        "uncertainty": uncertainty,
        "detectedText": "",
        "model": "MobileCLIP2-S2",
        "modelVersion": "apple/MobileCLIP2-S2",
        "catalogMatchAccepted": catalog_accepted,
        "matches": catalog_matches,
    }


def build_catalog_index(csv_path: str, output_path: str, catalog_root: str = "catalog") -> int:
    """Create a reusable image-embedding index from products.csv and reference photos."""
    state = _load_model()
    torch = state["torch"]
    Image = state["Image"]
    root = Path(catalog_root).resolve()
    products: list[dict] = []
    vectors = []
    with open(csv_path, newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        required = {"product_id", "name", "image_path"}
        if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
            raise ValueError("CSV must contain at least product_id, name, image_path columns.")
        for row_number, row in enumerate(reader, start=2):
            image_path = (root / row.get("image_path", "").strip()).resolve()
            if root not in image_path.parents and image_path != root:
                raise ValueError(f"Row {row_number}: image_path must stay inside the catalog directory.")
            if not image_path.is_file():
                raise ValueError(f"Row {row_number}: image not found: {image_path}")
            try:
                with Image.open(image_path) as source:
                    tensor = state["preprocess"](source.convert("RGB")).unsqueeze(0)
            except Exception as exc:
                raise ValueError(f"Row {row_number}: cannot decode {image_path.name}") from exc
            with torch.inference_mode():
                vector = state["model"].encode_image(tensor)
                vector = vector / vector.norm(dim=-1, keepdim=True).clamp_min(1e-12)
            vectors.append(vector.squeeze(0).cpu())
            products.append({
                "product_id": row.get("product_id", "").strip(),
                "sku": row.get("sku", "").strip(),
                "name": row.get("name", "").strip(),
                "category": row.get("category", "").strip(),
                "brand": row.get("brand", "").strip(),
                "dimensions": row.get("dimensions", "").strip(),
                "price": row.get("price", "").strip(),
                "image_path": row.get("image_path", "").strip(),
            })
    if not products:
        raise ValueError("No catalog products found. Add rows and reference images before indexing.")
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"model": "MobileCLIP2-S2", "products": products, "embeddings": torch.stack(vectors)}, out)
    return len(products)
