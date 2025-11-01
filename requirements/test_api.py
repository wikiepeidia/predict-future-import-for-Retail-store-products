import requests
import os
import sys  # Added for sys.exit()

# Test the CNN model with an invoice image
url = 'http://localhost:5000/api/model1/detect'
image_path = 'uploads/1761921663.454565_4949445_Capture.png'

print(f"Testing CNN model with image: {image_path}")
print(f"Image exists: {os.path.exists(image_path)}")

if os.path.exists(image_path):
    try:
        with open(image_path, 'rb') as f:
            files = {'file': f}
            print("Sending request to CNN model...")
            response = requests.post(url, files=files, timeout=10)  # Added timeout of 10 seconds
            print(f'Status Code: {response.status_code}')
            if response.status_code == 200:
                result = response.json()
                print('Response:')
                print(f"Success: {result.get('success', False)}")
                if 'data' in result:
                    data = result['data']
                    print(f"Products extracted: {len(data.get('products', []))}")
                    for i, product in enumerate(data.get('products', [])[:3]):  # Show first 3
                        print(f"  Product {i+1}: {product.get('product_name', 'N/A')} - Qty: {product.get('quantity', 0)} - Price: {product.get('unit_price', 0)}")
                else:
                    print("No data in response")
            else:
                print(f"Error response: {response.text}")
    except requests.exceptions.Timeout:
        print("Request timed out. Terminating.")
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("URL unreachable. Terminating.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
else:
    print('Image file not found')