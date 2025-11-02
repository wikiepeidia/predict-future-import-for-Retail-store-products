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
        """
        Danh sách sản phẩm Quán Sơn
        🔥 EXPANDED: 10 → 42 products with categories
        """
        return [
            # BEVERAGES (15 products)
            {'id': 'SON001', 'name': 'Cà phê đen', 'price': 15000, 'category': 'beverage'},
            {'id': 'SON002', 'name': 'Cà phê sữa', 'price': 18000, 'category': 'beverage'},
            {'id': 'SON003', 'name': 'Nước cam', 'price': 25000, 'category': 'beverage'},
            {'id': 'SON004', 'name': 'Trà đá', 'price': 5000, 'category': 'beverage'},
            {'id': 'SON005', 'name': 'Nước suối', 'price': 10000, 'category': 'beverage'},
            {'id': 'SON006', 'name': 'Sữa Brand A', 'price': 12000, 'category': 'beverage'},
            {'id': 'SON007', 'name': 'Trà sữa', 'price': 22000, 'category': 'beverage'},
            {'id': 'SON008', 'name': 'Sinh tố bơ', 'price': 28000, 'category': 'beverage'},
            {'id': 'SON009', 'name': 'Coca Cola', 'price': 15000, 'category': 'beverage'},
            {'id': 'SON010', 'name': 'Pepsi', 'price': 15000, 'category': 'beverage'},
            {'id': 'SON011', 'name': 'Sting dâu', 'price': 12000, 'category': 'beverage'},
            {'id': 'SON012', 'name': 'Red Bull', 'price': 18000, 'category': 'beverage'},
            {'id': 'SON013', 'name': 'Nước chanh', 'price': 20000, 'category': 'beverage'},
            {'id': 'SON014', 'name': 'Soda chanh', 'price': 22000, 'category': 'beverage'},
            {'id': 'SON015', 'name': 'Nước dừa', 'price': 25000, 'category': 'beverage'},
            
            # FOOD (15 products)
            {'id': 'SON016', 'name': 'Bánh mì thịt', 'price': 20000, 'category': 'food'},
            {'id': 'SON017', 'name': 'Bánh mì chả', 'price': 18000, 'category': 'food'},
            {'id': 'SON018', 'name': 'Bánh mì pate', 'price': 16000, 'category': 'food'},
            {'id': 'SON019', 'name': 'Phở bò', 'price': 45000, 'category': 'food'},
            {'id': 'SON020', 'name': 'Bún chả', 'price': 40000, 'category': 'food'},
            {'id': 'SON021', 'name': 'Cơm gà', 'price': 35000, 'category': 'food'},
            {'id': 'SON022', 'name': 'Xôi xéo', 'price': 18000, 'category': 'food'},
            {'id': 'SON023', 'name': 'Bánh bao', 'price': 12000, 'category': 'food'},
            {'id': 'SON024', 'name': 'Bánh cuốn', 'price': 25000, 'category': 'food'},
            {'id': 'SON025', 'name': 'Bánh giò', 'price': 15000, 'category': 'food'},
            {'id': 'SON026', 'name': 'Nem rán', 'price': 30000, 'category': 'food'},
            {'id': 'SON027', 'name': 'Gỏi cuốn', 'price': 25000, 'category': 'food'},
            {'id': 'SON028', 'name': 'Chả giò', 'price': 35000, 'category': 'food'},
            {'id': 'SON029', 'name': 'Mì xào', 'price': 32000, 'category': 'food'},
            {'id': 'SON030', 'name': 'Hủ tiếu', 'price': 38000, 'category': 'food'},
            
            # SNACKS (8 products)
            {'id': 'SON031', 'name': 'Snack khoai tây', 'price': 15000, 'category': 'snack'},
            {'id': 'SON032', 'name': 'Bánh ngọt', 'price': 30000, 'category': 'snack'},
            {'id': 'SON033', 'name': 'Kẹo', 'price': 8000, 'category': 'snack'},
            {'id': 'SON034', 'name': 'Socola Kitkat', 'price': 12000, 'category': 'snack'},
            {'id': 'SON035', 'name': 'Bánh quy', 'price': 18000, 'category': 'snack'},
            {'id': 'SON036', 'name': 'Khoai tây lát', 'price': 10000, 'category': 'snack'},
            {'id': 'SON037', 'name': 'Popcorn', 'price': 15000, 'category': 'snack'},
            {'id': 'SON038', 'name': 'Oreo', 'price': 20000, 'category': 'snack'},
            
            # CONDIMENTS (4 products)
            {'id': 'SON039', 'name': 'Tương ớt', 'price': 12000, 'category': 'condiment'},
            {'id': 'SON040', 'name': 'Nước mắm', 'price': 15000, 'category': 'condiment'},
            {'id': 'SON041', 'name': 'Dầu ăn', 'price': 45000, 'category': 'condiment'},
            {'id': 'SON042', 'name': 'Muối tiêu', 'price': 8000, 'category': 'condiment'},
        ]
    
    def _init_products_tung(self):
        """
        Danh sách sản phẩm Quán Tùng  
        🔥 EXPANDED: 10 → 45 products with categories
        """
        return [
            # BABY PRODUCTS (15 products)
            {'id': 'TUNG001', 'name': 'Sữa Brand A', 'price': 50000, 'category': 'beverage'},
            {'id': 'TUNG002', 'name': 'Sản phẩm Thai sản Brand B', 'price': 120000, 'category': 'other'},
            {'id': 'TUNG003', 'name': 'Bỉm trẻ em', 'price': 85000, 'category': 'other'},
            {'id': 'TUNG004', 'name': 'Sữa bột', 'price': 350000, 'category': 'beverage'},
            {'id': 'TUNG005', 'name': 'Tã giấy', 'price': 45000, 'category': 'other'},
            {'id': 'TUNG006', 'name': 'Bình sữa', 'price': 95000, 'category': 'other'},
            {'id': 'TUNG007', 'name': 'Núm ty', 'price': 35000, 'category': 'other'},
            {'id': 'TUNG008', 'name': 'Khăn tắm em bé', 'price': 55000, 'category': 'other'},
            {'id': 'TUNG009', 'name': 'Kem chống hăm', 'price': 68000, 'category': 'other'},
            {'id': 'TUNG010', 'name': 'Dầu massage bé', 'price': 72000, 'category': 'other'},
            {'id': 'TUNG011', 'name': 'Phấn rôm', 'price': 42000, 'category': 'other'},
            {'id': 'TUNG012', 'name': 'Nước tắm bé', 'price': 58000, 'category': 'other'},
            {'id': 'TUNG013', 'name': 'Bộ đồ cho bé', 'price': 120000, 'category': 'other'},
            {'id': 'TUNG014', 'name': 'Gạc sữa', 'price': 28000, 'category': 'other'},
            {'id': 'TUNG015', 'name': 'Khăn ướt', 'price': 38000, 'category': 'other'},
            
            # HEALTH & BEAUTY (15 products)
            {'id': 'TUNG016', 'name': 'Vitamin tổng hợp', 'price': 150000, 'category': 'other'},
            {'id': 'TUNG017', 'name': 'Kem dưỡng da', 'price': 95000, 'category': 'other'},
            {'id': 'TUNG018', 'name': 'Dầu gội', 'price': 65000, 'category': 'other'},
            {'id': 'TUNG019', 'name': 'Sữa tắm', 'price': 55000, 'category': 'other'},
            {'id': 'TUNG020', 'name': 'Kem chống nắng', 'price': 180000, 'category': 'other'},
            {'id': 'TUNG021', 'name': 'Sữa rửa mặt', 'price': 85000, 'category': 'other'},
            {'id': 'TUNG022', 'name': 'Nước hoa hồng', 'price': 120000, 'category': 'other'},
            {'id': 'TUNG023', 'name': 'Serum dưỡng', 'price': 250000, 'category': 'other'},
            {'id': 'TUNG024', 'name': 'Mặt nạ giấy', 'price': 45000, 'category': 'other'},
            {'id': 'TUNG025', 'name': 'Tẩy trang', 'price': 95000, 'category': 'other'},
            {'id': 'TUNG026', 'name': 'Kem dưỡng môi', 'price': 35000, 'category': 'other'},
            {'id': 'TUNG027', 'name': 'Sữa dưỡng thể', 'price': 110000, 'category': 'other'},
            {'id': 'TUNG028', 'name': 'Nước súc miệng', 'price': 48000, 'category': 'other'},
            {'id': 'TUNG029', 'name': 'Kem đánh răng', 'price': 32000, 'category': 'other'},
            {'id': 'TUNG030', 'name': 'Bàn chải đánh răng', 'price': 22000, 'category': 'other'},
            
            # HOUSEHOLD (10 products)
            {'id': 'TUNG031', 'name': 'Khăn giấy', 'price': 25000, 'category': 'other'},
            {'id': 'TUNG032', 'name': 'Giấy vệ sinh', 'price': 35000, 'category': 'other'},
            {'id': 'TUNG033', 'name': 'Nước rửa chén', 'price': 42000, 'category': 'condiment'},
            {'id': 'TUNG034', 'name': 'Nước giặt', 'price': 88000, 'category': 'condiment'},
            {'id': 'TUNG035', 'name': 'Nước lau sàn', 'price': 55000, 'category': 'condiment'},
            {'id': 'TUNG036', 'name': 'Xịt phòng', 'price': 62000, 'category': 'other'},
            {'id': 'TUNG037', 'name': 'Túi rác', 'price': 28000, 'category': 'other'},
            {'id': 'TUNG038', 'name': 'Miếng rửa chén', 'price': 15000, 'category': 'other'},
            {'id': 'TUNG039', 'name': 'Găng tay cao su', 'price': 18000, 'category': 'other'},
            {'id': 'TUNG040', 'name': 'Nến thơm', 'price': 45000, 'category': 'other'},
            
            # SNACKS & DRINKS (5 products)
            {'id': 'TUNG041', 'name': 'Bánh ăn dặm', 'price': 68000, 'category': 'snack'},
            {'id': 'TUNG042', 'name': 'Nước ép trái cây', 'price': 35000, 'category': 'beverage'},
            {'id': 'TUNG043', 'name': 'Sữa chua uống', 'price': 28000, 'category': 'beverage'},
            {'id': 'TUNG044', 'name': 'Ngũ cốc dinh dưỡng', 'price': 95000, 'category': 'food'},
            {'id': 'TUNG045', 'name': 'Bánh quy cho bé', 'price': 42000, 'category': 'snack'},
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
        Generate structured invoice data with REALISTIC patterns
        This represents Y1 output (hóa đơn điện tử)
        
        🔥 IMPROVEMENT: Added seasonal, weekly, and category-based quantity logic
        """
        products_list = self.products_son if store_type == 'son' else self.products_tung
        store_name = "Quán Sơn" if store_type == 'son' else "Quán Tùng"
        
        # Random number of products (2-6)
        num_products = random.randint(2, 6)
        selected_products = random.sample(products_list, num_products)
        
        # 🔥 IMPROVEMENT: Extract seasonal and time patterns
        month = date.month
        day_of_week = date.weekday()  # 0=Monday, 6=Sunday
        is_weekend = day_of_week >= 5
        is_summer = month in [6, 7, 8]
        is_winter = month in [12, 1, 2]
        
        products = []
        for prod in selected_products:
            # 🔥 IMPROVEMENT: Category-based base quantities
            category = prod.get('category', 'other')
            base_qty_map = {
                'beverage': 80,
                'food': 50,
                'snack': 40,
                'condiment': 25,
                'other': 30
            }
            base_qty = base_qty_map.get(category, 30)
            
            # 🔥 IMPROVEMENT: Seasonal adjustments
            if category == 'beverage' and is_summer:
                base_qty = int(base_qty * 1.6)  # 60% boost in summer
            elif category == 'food' and is_winter:
                base_qty = int(base_qty * 1.3)  # 30% boost in winter
            
            # 🔥 IMPROVEMENT: Weekend boost
            if is_weekend:
                base_qty = int(base_qty * 1.4)  # 40% more on weekends
            
            # 🔥 IMPROVEMENT: Random variation ±25% (more realistic than ±90%)
            quantity = int(base_qty * random.uniform(0.75, 1.25))
            quantity = max(5, quantity)  # Minimum 5 units
            
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
