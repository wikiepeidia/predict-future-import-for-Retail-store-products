"""
Generate synthetic dataset for training
3 DATASET:
1. Danh sách sản phẩm quán Sơn
2. Danh sách sản phẩm quán Tùng  
3. Hóa đơn điện tử quán Tùng

Split: 70% train, 10% valid, 20% test
"""

import os
import json
import numpy as np
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import random

class DatasetGenerator:
    """Generate synthetic dataset for training CNN and LSTM models"""
    
    def __init__(self, output_dir='data'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(f"{output_dir}/images", exist_ok=True)
        os.makedirs(f"{output_dir}/invoices", exist_ok=True)
        
        # Product catalogs
        self.products_son = self._init_products_son()
        self.products_tung = self._init_products_tung()
        
    def _init_products_son(self):
        """Danh sách sản phẩm Quán Sơn"""
        return [
            {'id': 'SON001', 'name': 'Cà phê đen', 'price': 15000},
            {'id': 'SON002', 'name': 'Cà phê sữa', 'price': 18000},
            {'id': 'SON003', 'name': 'Bánh mì thịt', 'price': 20000},
            {'id': 'SON004', 'name': 'Nước cam', 'price': 25000},
            {'id': 'SON005', 'name': 'Trà đá', 'price': 5000},
            {'id': 'SON006', 'name': 'Sữa Brand A', 'price': 12000},
            {'id': 'SON007', 'name': 'Bánh ngọt', 'price': 30000},
            {'id': 'SON008', 'name': 'Nước suối', 'price': 10000},
            {'id': 'SON009', 'name': 'Snack', 'price': 15000},
            {'id': 'SON010', 'name': 'Kẹo', 'price': 8000},
        ]
    
    def _init_products_tung(self):
        """Danh sách sản phẩm Quán Tùng"""
        return [
            {'id': 'TUNG001', 'name': 'Sữa Brand A', 'price': 50000},
            {'id': 'TUNG002', 'name': 'Sản phẩm Thai sản Brand B', 'price': 120000},
            {'id': 'TUNG003', 'name': 'Bỉm trẻ em', 'price': 85000},
            {'id': 'TUNG004', 'name': 'Sữa bột', 'price': 350000},
            {'id': 'TUNG005', 'name': 'Tã giấy', 'price': 45000},
            {'id': 'TUNG006', 'name': 'Vitamin tổng hợp', 'price': 150000},
            {'id': 'TUNG007', 'name': 'Kem dưỡng da', 'price': 95000},
            {'id': 'TUNG008', 'name': 'Dầu gội', 'price': 65000},
            {'id': 'TUNG009', 'name': 'Sữa tắm', 'price': 55000},
            {'id': 'TUNG010', 'name': 'Khăn giấy', 'price': 25000},
        ]
    
    def generate_invoice_image(self, invoice_data, filename):
        """
        Generate synthetic invoice image (hóa đơn giấy)
        This simulates x1 input for Model 1
        """
        # Create blank invoice
        img = Image.new('RGB', (800, 1000), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            # Try to use a font
            font_title = ImageFont.truetype("arial.ttf", 24)
            font_text = ImageFont.truetype("arial.ttf", 16)
            font_small = ImageFont.truetype("arial.ttf", 12)
        except:
            # Fallback to default font
            font_title = ImageFont.load_default()
            font_text = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Header
        store_name = invoice_data['store_name']
        draw.text((300, 30), f"{store_name}", fill='black', font=font_title)
        draw.text((250, 70), "HOA DON NHAP HANG", fill='black', font=font_text)
        
        # Invoice info
        y = 120
        draw.text((50, y), f"Ma hoa don: {invoice_data['invoice_id']}", fill='black', font=font_text)
        y += 30
        draw.text((50, y), f"Ngay: {invoice_data['date']}", fill='black', font=font_text)
        
        # Table header
        y += 50
        draw.line([(50, y), (750, y)], fill='black', width=2)
        y += 10
        draw.text((60, y), "STT", fill='black', font=font_text)
        draw.text((150, y), "San pham", fill='black', font=font_text)
        draw.text((450, y), "So luong", fill='black', font=font_text)
        draw.text((580, y), "Don gia", fill='black', font=font_text)
        y += 25
        draw.line([(50, y), (750, y)], fill='black', width=1)
        
        # Products
        for idx, product in enumerate(invoice_data['products'], 1):
            y += 25
            draw.text((60, y), str(idx), fill='black', font=font_small)
            draw.text((150, y), product['product_name'], fill='black', font=font_small)
            draw.text((450, y), str(product['quantity']), fill='black', font=font_small)
            draw.text((580, y), f"{product['unit_price']:,}", fill='black', font=font_small)
        
        # Total
        y += 40
        draw.line([(50, y), (750, y)], fill='black', width=2)
        y += 15
        draw.text((450, y), "TONG CONG:", fill='black', font=font_text)
        draw.text((580, y), f"{invoice_data['total_amount']:,} VND", fill='black', font=font_text)
        
        # Save
        filepath = os.path.join(self.output_dir, 'images', filename)
        img.save(filepath)
        return filepath
    
    def generate_invoice_data(self, store_type, date, invoice_id):
        """
        Generate structured invoice data
        This represents Y1 output (hóa đơn điện tử)
        """
        products_list = self.products_son if store_type == 'son' else self.products_tung
        store_name = "Quán Sơn" if store_type == 'son' else "Quán Tùng"
        
        # Random number of products (2-6)
        num_products = random.randint(2, 6)
        selected_products = random.sample(products_list, num_products)
        
        products = []
        for prod in selected_products:
            quantity = random.randint(10, 200)
            products.append({
                'product_id': prod['id'],
                'product_name': prod['name'],
                'quantity': quantity,
                'unit_price': prod['price'],
                'line_total': quantity * prod['price']
            })
        
        total_amount = sum(p['line_total'] for p in products)
        
        return {
            'invoice_id': invoice_id,
            'store_name': store_name,
            'store_type': store_type,
            'date': date.isoformat(),
            'products': products,
            'total_amount': total_amount
        }
    
    def generate_full_dataset(self, num_samples=1000):
        """
        Generate complete dataset with train/valid/test split
        70% train, 10% valid, 20% test
        """
        print(f"Generating {num_samples} samples...")
        
        dataset = {
            'son': [],  # Quán Sơn
            'tung': []  # Quán Tùng
        }
        
        start_date = datetime.now() - timedelta(days=365)
        
        for i in range(num_samples):
            # Alternate between stores
            store_type = 'son' if i % 2 == 0 else 'tung'
            
            # Generate date
            date = start_date + timedelta(days=i * 365 // num_samples)
            invoice_id = f"INV_{store_type.upper()}_{i:05d}"
            
            # Generate invoice data
            invoice_data = self.generate_invoice_data(store_type, date, invoice_id)
            
            # Generate invoice image
            image_filename = f"{invoice_id}.png"
            self.generate_invoice_image(invoice_data, image_filename)
            invoice_data['image_path'] = f"images/{image_filename}"
            
            # Add to dataset
            dataset[store_type].append(invoice_data)
            
            if (i + 1) % 100 == 0:
                print(f"Generated {i + 1}/{num_samples} samples...")
        
        # Split dataset
        splits = self._split_dataset(dataset)
        
        # Save datasets
        self._save_datasets(splits)
        
        print(f"\n✅ Dataset generation complete!")
        print(f"Total samples: {num_samples}")
        print(f"Train: {len(splits['train'])} (70%)")
        print(f"Valid: {len(splits['valid'])} (10%)")
        print(f"Test: {len(splits['test'])} (20%)")
        
        return splits
    
    def _split_dataset(self, dataset):
        """Split dataset into train/valid/test (70/10/20)"""
        all_invoices = dataset['son'] + dataset['tung']
        
        # Shuffle
        random.shuffle(all_invoices)
        
        # Calculate split indices
        total = len(all_invoices)
        train_end = int(total * 0.7)
        valid_end = int(total * 0.8)
        
        return {
            'train': all_invoices[:train_end],
            'valid': all_invoices[train_end:valid_end],
            'test': all_invoices[valid_end:]
        }
    
    def _save_datasets(self, splits):
        """Save datasets to JSON files"""
        for split_name, data in splits.items():
            filepath = os.path.join(self.output_dir, 'invoices', f'{split_name}.json')
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Saved {split_name}: {filepath}")
        
        # Save product catalogs
        catalogs = {
            'son': self.products_son,
            'tung': self.products_tung
        }
        catalog_path = os.path.join(self.output_dir, 'product_catalogs.json')
        with open(catalog_path, 'w', encoding='utf-8') as f:
            json.dump(catalogs, f, ensure_ascii=False, indent=2)
        print(f"Saved product catalogs: {catalog_path}")


if __name__ == "__main__":
    # Generate dataset
    generator = DatasetGenerator(output_dir='data')
    
    print("=" * 60)
    print("DATASET GENERATION")
    print("3 DATASET:")
    print("1. Danh sách sản phẩm quán Sơn")
    print("2. Danh sách sản phẩm quán Tùng")
    print("3. Hóa đơn điện tử quán Tùng")
    print("=" * 60)
    
    splits = generator.generate_full_dataset(num_samples=300)
    
    print("\n✅ Dataset ready for training!")
    print("Location: data/")
