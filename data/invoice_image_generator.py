# -*- coding: utf-8 -*-
"""
Invoice Image Generator
Generates synthetic invoice images from DATASET-tung1000.csv for CNN training
"""
import os
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import random
from pathlib import Path


class InvoiceImageGenerator:
    """Generate synthetic invoice images from product data"""
    
    def __init__(self, csv_path='data/QUANSON.csv', output_dir='data/generated_invoices_quanson'):
        """
        Initialize generator
        
        Args:
            csv_path: Path to product CSV (QUANSON.csv or QUANTUNG.csv)
            output_dir: Directory to save generated images
        """
        self.csv_path = csv_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load product data
        print(f"Loading product data from {csv_path}...")
        self.df = pd.read_csv(csv_path, encoding='utf-8')
        print(f"Loaded {len(self.df)} products")
        
        # Warehouse/Store names based on dataset
        if 'QUANSON' in csv_path.upper():
            self.templates = [
                "Kho Quân Sơn - Chi nhánh HN",
                "Kho Quân Sơn - Chi nhánh HCM", 
                "Kho Quân Sơn - Trung tâm",
                "Kho Quân Sơn - Phân phối",
                "Kho Quân Sơn - Bán sỉ"
            ]
        elif 'QUANTUNG' in csv_path.upper():
            self.templates = [
                "Kho Quân Tùng - Chi nhánh 1",
                "Kho Quân Tùng - Chi nhánh 2", 
                "Kho Quân Tùng - Bán lẻ",
                "Kho Quân Tùng - Showroom",
                "Kho Quân Tùng - Trung tâm"
            ]
        else:
            self.templates = [
                "Cửa hàng Tạp hóa ABC",
                "Siêu thị Mini XYZ", 
                "Cửa hàng Tiện lợi 123"
            ]
        
    def generate_invoice_image(self, num_products=None, width=800, height=1000):
        """
        Generate a single invoice image
        
        Args:
            num_products: Number of products (random 3-10 if None)
            width: Image width
            height: Image height
            
        Returns:
            PIL.Image: Generated invoice image
            dict: Invoice data
        """
        if num_products is None:
            num_products = random.randint(3, 10)
        
        # Create blank image (white background)
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        # Try to use a font, fallback to default
        try:
            font_title = ImageFont.truetype("arial.ttf", 32)
            font_header = ImageFont.truetype("arial.ttf", 20)
            font_text = ImageFont.truetype("arial.ttf", 16)
        except:
            font_title = ImageFont.load_default()
            font_header = ImageFont.load_default()
            font_text = ImageFont.load_default()
        
        y_position = 30
        
        # Store name (header)
        store_name = random.choice(self.templates)
        draw.text((width//2 - 150, y_position), store_name, fill='black', font=font_title)
        y_position += 50
        
        # Invoice ID
        invoice_id = f"INV{random.randint(10000, 99999)}"
        draw.text((50, y_position), f"Hóa đơn: {invoice_id}", fill='black', font=font_header)
        y_position += 40
        
        # Date
        draw.text((50, y_position), f"Ngày: {random.randint(1,28)}/{random.randint(1,12)}/2024", 
                 fill='black', font=font_text)
        y_position += 40
        
        # Separator line
        draw.line([(50, y_position), (width-50, y_position)], fill='black', width=2)
        y_position += 20
        
        # Table header
        draw.text((50, y_position), "Sản phẩm", fill='black', font=font_header)
        draw.text((400, y_position), "SL", fill='black', font=font_header)
        draw.text((500, y_position), "Đơn giá", fill='black', font=font_header)
        draw.text((650, y_position), "Thành tiền", fill='black', font=font_header)
        y_position += 35
        
        # Separator line
        draw.line([(50, y_position), (width-50, y_position)], fill='gray', width=1)
        y_position += 10
        
        # Select random products
        selected_products = self.df.sample(n=min(num_products, len(self.df)))
        
        products_data = []
        total_amount = 0
        
        for _, product in selected_products.iterrows():
            product_name = product['Tên sản phẩm']
            
            # Fix: Remove dots from price (40.000 -> 40000)
            retail_price_str = str(product['PL_Giá bán lẻ']).replace('.', '').replace(',', '')
            try:
                retail_price = int(float(retail_price_str))
            except:
                retail_price = 10000  # Default price if parsing fails
            
            quantity = random.randint(1, 20)
            line_total = quantity * retail_price
            total_amount += line_total
            
            # Truncate long product names
            if len(product_name) > 30:
                product_name = product_name[:27] + "..."
            
            # Draw product line
            draw.text((50, y_position), product_name, fill='black', font=font_text)
            draw.text((400, y_position), str(quantity), fill='black', font=font_text)
            draw.text((500, y_position), f"{retail_price:,}", fill='black', font=font_text)
            draw.text((650, y_position), f"{line_total:,}", fill='black', font=font_text)
            y_position += 25
            
            products_data.append({
                'product_name': product['Tên sản phẩm'],
                'category': product['Loại sản phẩm'],
                'sku': product['Mã SKU'],
                'quantity': quantity,
                'unit_price': retail_price,
                'line_total': line_total
            })
        
        # Separator line
        y_position += 10
        draw.line([(50, y_position), (width-50, y_position)], fill='black', width=2)
        y_position += 20
        
        # Total
        draw.text((500, y_position), "TỔNG CỘNG:", fill='black', font=font_header)
        draw.text((650, y_position), f"{total_amount:,} VNĐ", fill='red', font=font_header)
        
        # Add some noise/variation to make it realistic
        img_array = np.array(img)
        
        # Add slight noise
        noise = np.random.randint(-10, 10, img_array.shape, dtype=np.int16)
        img_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
        
        # Optional: Add slight rotation
        img = Image.fromarray(img_array)
        rotation_angle = random.uniform(-2, 2)
        img = img.rotate(rotation_angle, fillcolor='white', expand=False)
        
        invoice_data = {
            'invoice_id': invoice_id,
            'store_name': store_name,
            'products': products_data,
            'total_amount': total_amount,
            'num_products': len(products_data)
        }
        
        return img, invoice_data
    
    def generate_dataset(self, num_images=100, split_ratio=0.8):
        """
        Generate a dataset of invoice images
        
        Args:
            num_images: Number of images to generate
            split_ratio: Train/test split ratio
            
        Returns:
            dict: Paths to train and test directories
        """
        print(f"\nGenerating {num_images} invoice images...")
        
        # Create directories
        train_dir = self.output_dir / 'train'
        test_dir = self.output_dir / 'test'
        train_dir.mkdir(exist_ok=True)
        test_dir.mkdir(exist_ok=True)
        
        train_data = []
        test_data = []
        
        num_train = int(num_images * split_ratio)
        
        for i in range(num_images):
            # Generate image
            img, invoice_data = self.generate_invoice_image()
            
            # Determine train/test
            if i < num_train:
                output_dir = train_dir
                data_list = train_data
                prefix = 'train'
            else:
                output_dir = test_dir
                data_list = test_data
                prefix = 'test'
            
            # Save image
            img_path = output_dir / f"invoice_{i:04d}.png"
            img.save(img_path)
            
            # Save metadata
            invoice_data['image_path'] = str(img_path)
            data_list.append(invoice_data)
            
            if (i + 1) % 20 == 0:
                print(f"  Generated {i + 1}/{num_images} images...")
        
        # Save metadata as JSON
        import json
        
        train_json = self.output_dir / 'train_metadata.json'
        test_json = self.output_dir / 'test_metadata.json'
        
        with open(train_json, 'w', encoding='utf-8') as f:
            json.dump(train_data, f, ensure_ascii=False, indent=2)
        
        with open(test_json, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Dataset generation complete!")
        print(f"  Train images: {len(train_data)} ({train_dir})")
        print(f"  Test images: {len(test_data)} ({test_dir})")
        print(f"  Metadata: {train_json}, {test_json}")
        
        return {
            'train_dir': str(train_dir),
            'test_dir': str(test_dir),
            'train_metadata': str(train_json),
            'test_metadata': str(test_json),
            'num_train': len(train_data),
            'num_test': len(test_data)
        }


def main():
    """Generate sample dataset from BOTH warehouses"""
    print("="*60)
    print("Invoice Image Generator")
    print("Generating synthetic invoices from QUANTUNG + QUANSON")
    print("="*60)
    
    # Generate from QUANSON (100 images - larger warehouse)
    print("\n[1/2] Generating from QUANSON (14,142 products)...")
    generator_quanson = InvoiceImageGenerator(csv_path='data/QUANSON.csv')
    result_quanson = generator_quanson.generate_dataset(num_images=100, split_ratio=0.8)
    
    # Generate from QUANTUNG (100 images - smaller warehouse)
    print("\n[2/2] Generating from QUANTUNG (959 products)...")
    generator_quantung = InvoiceImageGenerator(
        csv_path='data/QUANTUNG.csv',
        output_dir='data/generated_invoices_quantung'
    )
    result_quantung = generator_quantung.generate_dataset(num_images=100, split_ratio=0.8)
    
    print("\n" + "="*60)
    print("Dataset ready for CNN training!")
    print("="*60)
    print(f"\n✅ QUANSON Dataset:")
    print(f"   Train: {result_quanson['num_train']} images")
    print(f"   Test: {result_quanson['num_test']} images")
    print(f"   Metadata: {result_quanson['train_metadata']}")
    
    print(f"\n✅ QUANTUNG Dataset:")
    print(f"   Train: {result_quantung['num_train']} images")
    print(f"   Test: {result_quantung['num_test']} images")
    print(f"   Metadata: {result_quantung['train_metadata']}")
    
    print(f"\n📊 Total: {result_quanson['num_train'] + result_quantung['num_train']} train + {result_quanson['num_test'] + result_quantung['num_test']} test images")
    
    print("\nYou can now train the CNN model:")
    print("  python train_models.py")
    
    return {
        'quanson': result_quanson,
        'quantung': result_quantung
    }


if __name__ == "__main__":
    main()
