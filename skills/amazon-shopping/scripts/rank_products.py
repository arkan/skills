#!/usr/bin/env python3
"""
Amazon Product Ranking Script

Analyzes collected Amazon product data from JSONL files and ranks items
based on user preferences. Prioritizes review count over rating when
ratings are similar.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any


def parse_review_count(review_str: str) -> int:
    """Parse various Amazon review count formats."""
    if isinstance(review_str, int):
        return review_str
    if not review_str:
        return 0
    # Remove commas and extract digits
    cleaned = str(review_str).replace(',', '').replace('ratings', '').replace('rating', '').strip()
    try:
        return int(cleaned)
    except ValueError:
        return 0


def load_products(jsonl_path: str) -> List[Dict[str, Any]]:
    """Load products from JSONL file."""
    products = []
    with open(jsonl_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    products.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return products


def calculate_score(product: Dict[str, Any], priority: str, max_budget: float = None) -> float:
    """Calculate a score for a product based on priority and constraints."""
    # Filter by budget first
    if max_budget is not None:
        price = product.get('price', 0)
        if isinstance(price, str):
            price = float(price.replace('$', '').replace(',', '').strip())
        if price > max_budget:
            return -1  # Disqualified

    score = 0.0
    rating = product.get('rating', 0)
    reviews = product.get('review_count', 0)
    if isinstance(reviews, str):
        reviews = parse_review_count(reviews)

    # Base score from rating (0-50 points)
    score += (rating / 5.0) * 50

    # Review count bonus (diminishing returns, up to 30 points)
    # Log scale: 100 reviews = ~15 points, 1000 = ~22 points, 10000 = ~30 points
    if reviews > 0:
        import math
        review_bonus = min(30, math.log10(max(1, reviews)) * 7.5)
        score += review_bonus

    # Apply priority multiplier
    if priority == 'rating':
        score = score * 1.2 + (rating * 10)
    elif priority == 'reviews':
        score = score * 1.3 + (min(30, math.log10(max(1, reviews)) * 10))
    elif priority == 'price':
        price = product.get('price', 0)
        if isinstance(price, str):
            price = float(price.replace('$', '').replace(',', '').strip())
        # Lower is better - invert score
        if price > 0:
            price_bonus = max(0, 20 - (price / max_budget * 20 if max_budget else price / 100))
            score += price_bonus

    # Prime bonus (5 points)
    if product.get('is_prime'):
        score += 5

    # Sponsored penalty (3 points - still consider but demote)
    if product.get('is_sponsored'):
        score -= 3

    return score


def compare_by_rating_then_reviews(products: List[Dict]) -> List[Dict]:
    """
    Sort products prioritizing rating, but when ratings are similar
    (within 0.5 stars), prioritize review count.
    """
    def sort_key(p):
        rating = p.get('rating', 0)
        reviews = p.get('review_count', 0)
        if isinstance(reviews, str):
            reviews = parse_review_count(reviews)
        # Primary: rating, Secondary: reviews (for tie-breaking)
        return (-rating, -reviews)

    return sorted(products, key=sort_key)


def rank_products(products: List[Dict], priority: str = 'rating', max_budget: float = None) -> List[Dict]:
    """Rank products and add scores."""
    scored = []
    for p in products:
        score = calculate_score(p, priority, max_budget)
        if score >= 0:  # Only include non-disqualified items
            p['_score'] = score
            scored.append(p)

    # Sort by score, then apply rating+reviews tiebreaker
    ranked = sorted(scored, key=lambda p: -p['_score'])

    # Final pass: for items with similar scores, apply rating+reviews tiebreaker
    # Group items within 5 points of each other
    i = 0
    while i < len(ranked):
        j = i + 1
        while j < len(ranked) and abs(ranked[i]['_score'] - ranked[j]['_score']) < 5:
            j += 1
        # Sort this group by rating then reviews
        if j - i > 1:
            ranked[i:j] = compare_by_rating_then_reviews(ranked[i:j])
        i = j

    return ranked


def format_ranked_output(ranked: List[Dict], priority: str, max_budget: float = None) -> str:
    """Format ranked products for display."""
    output = []

    output.append(f"## Ranked Products")
    output.append(f"**Priority:** {priority}")
    if max_budget:
        output.append(f"**Budget:** ${max_budget:.2f}")
    output.append(f"**Items analyzed:** {len(ranked)}")
    output.append("")

    for i, product in enumerate(ranked[:10], 1):  # Top 10
        name = product.get('name', 'Unknown Product')
        price = product.get('price', 'N/A')
        rating = product.get('rating', 'N/A')
        reviews = product.get('review_count', 'N/A')
        url = product.get('url', '')
        score = product.get('_score', 0)

        output.append(f"### {i}. {name}")
        output.append(f"**Price:** ${price}")
        output.append(f"**Rating:** {rating}/5 ({reviews:,} reviews)" if isinstance(reviews, int) else f"**Rating:** {rating}/5 ({reviews} reviews)")
        output.append(f"**Score:** {score:.1f}/100")
        if url:
            output.append(f"**Link:** {url}")

        # Key specs
        specs = product.get('specs', {})
        if specs:
            output.append(f"**Specs:** {', '.join(f'{k}: {v}' for k, v in list(specs.items())[:3])}")

        # Features
        features = product.get('features', [])
        if features:
            output.append(f"**Features:** {', '.join(features[:3])}")

        output.append("")
        output.append("---")
        output.append("")

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description='Rank Amazon products by user preferences')
    parser.add_argument('jsonl_file', help='Path to JSONL file containing Amazon product data')
    parser.add_argument('--budget', type=float, help='Maximum budget')
    parser.add_argument('--priority', choices=['rating', 'price', 'reviews', 'features'],
                        default='rating', help='Ranking priority (default: rating)')
    parser.add_argument('--top', type=int, default=5, help='Number of top results to show (default: 5)')

    args = parser.parse_args()

    # Load products
    products = load_products(args.jsonl_file)
    if not products:
        print("No products found in JSONL file", file=sys.stderr)
        sys.exit(1)

    # Rank products
    ranked = rank_products(products, priority=args.priority, max_budget=args.budget)

    # Format and output
    output = format_ranked_output(ranked, args.priority, args.budget)
    print(output)


if __name__ == '__main__':
    main()
