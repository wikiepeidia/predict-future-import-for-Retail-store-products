"""
Invoice Processing Utilities
Handles product extraction and invoice data building
"""
import json
from datetime import datetime
from pathlib import Path
from .data_processor import (
    normalize_text, extract_quantity_from_line,
    extract_price_candidates, detect_store_from_text
)


def load_product_catalogs(catalog_file: Path):
    """Load product catalogs from JSON file"""
    if catalog_file.exists():
        try:
            with catalog_file.open('r', encoding='utf-8') as handle:
                data = json.load(handle)
                if isinstance(data, dict):
                    return data
        except (OSError, ValueError) as exc:
            print(f"Warning: Unable to load product catalogs ({exc})")
    return {}


def build_catalog_index(product_catalogs):
    """Build searchable index from product catalogs"""
    catalog_index = []
    for store_key, products in product_catalogs.items():
        for product in products:
            catalog_index.append({
                'store': store_key,
                'product': product,
                'name_normalized': normalize_text(product.get('name', ''))
            })
    return catalog_index


def lookup_catalog_price(catalog_index, product_id=None, product_name=None):
    """Lookup price in catalog by ID or name"""
    if product_id:
        for entry in catalog_index:
            if entry['product'].get('id') == product_id:
                return entry['product'].get('price', 0)
    
    if product_name:
        normalized_name = normalize_text(product_name)
        for entry in catalog_index:
            if entry['name_normalized'] == normalized_name:
                return entry['product'].get('price', 0)
    return 0


def extract_products_from_text(text, catalog_index):
    """Extract products from invoice text"""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    normalized_lines = [normalize_text(line) for line in lines]
    
    aggregated = {}
    store_counts = {}
    
    for original_line, normalized_line in zip(lines, normalized_lines):
        for entry in catalog_index:
            name_normalized = entry['name_normalized']
            if not name_normalized or name_normalized not in normalized_line:
                continue
            
            store_key = entry['store']
            store_counts[store_key] = store_counts.get(store_key, 0) + 1
            
            product = entry['product']
            product_id = product.get('id')
            
            if product_id not in aggregated:
                aggregated[product_id] = {
                    'product_id': product_id,
                    'product_name': product.get('name', 'Unknown Product'),
                    'quantity': 0,
                    'unit_price': product.get('price', 0),
                    'line_total': 0
                }
            
            record = aggregated[product_id]
            quantity = extract_quantity_from_line(original_line)
            if quantity:
                record['quantity'] += quantity
            
            prices = extract_price_candidates(original_line)
            if prices:
                candidate_unit = min(prices)
                if candidate_unit < record['unit_price'] * 5 and candidate_unit > 0:
                    record['unit_price'] = candidate_unit
                
                candidate_total = max(prices)
                if record['quantity']:
                    record['line_total'] = max(
                        record['line_total'],
                        candidate_total,
                        record['unit_price'] * record['quantity']
                    )
                else:
                    record['line_total'] = max(record['line_total'], candidate_total)
    
    # Finalize products
    products = []
    for record in aggregated.values():
        if record['quantity'] <= 0:
            record['quantity'] = 1
        if record['unit_price'] <= 0:
            record['unit_price'] = lookup_catalog_price(
                catalog_index,
                record.get('product_id'),
                record.get('product_name')
            ) or 10000
        
        line_estimate = record['unit_price'] * record['quantity']
        record['line_total'] = max(record['line_total'], line_estimate)
        record['quantity'] = int(round(record['quantity']))
        record['unit_price'] = int(round(record['unit_price']))
        record['line_total'] = int(round(record['line_total']))
        products.append(record)
    
    products.sort(key=lambda item: item['line_total'], reverse=True)
    return products[:12], store_counts


def build_invoice_data(ocr_result, catalog_index, product_catalogs, store_name_lookup):
    """Build structured invoice data from OCR result"""
    extracted_text = ocr_result.get('extracted_text', '') or ''
    parsed_data = ocr_result.get('parsed_data') or {}
    
    products, store_counts = extract_products_from_text(extracted_text, catalog_index)
    store_key = detect_store_from_text(extracted_text)
    
    if not store_key and store_counts:
        try:
            candidate_key, candidate_count = max(store_counts.items(), key=lambda item: item[1])
            if candidate_count > 0:
                store_key = candidate_key
        except ValueError:
            store_key = None
    
    if not products:
        store_key = store_key or 'son'
        catalog = product_catalogs.get(store_key, [])[:3]
        products = [{
            'product_id': p.get('id'),
            'product_name': p.get('name'),
            'quantity': 1,
            'unit_price': p.get('price', 0),
            'line_total': p.get('price', 0)
        } for p in catalog]
    
    store_name = store_name_lookup.get(store_key, 'Unknown Store')
    total_amount = sum(product.get('line_total', 0) for product in products)
    
    invoice_identifier = parsed_data.get('invoice_number') or f"INV_{int(datetime.now().timestamp())}"
    
    return {
        'invoice_id': invoice_identifier,
        'store_name': store_name,
        'store_key': store_key,
        'products': products,
        'total_amount': int(round(total_amount)),
        'detection_confidence': float(ocr_result.get('confidence', 0.85)),
        'text_regions_count': max(len(products), 1),
        'extracted_text': extracted_text,
        'date': datetime.now().isoformat()
    }
