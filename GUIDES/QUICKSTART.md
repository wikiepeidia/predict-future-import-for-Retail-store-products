# 🚀 Quick Start Guide

## Chạy ứng dụng trong 3 bước

### Bước 1: Cài đặt dependencies
```powershell
pip install flask flask-login
```

### Bước 2: Khởi tạo database
```powershell
python create_database.py
```

### Bước 3: Chạy server
```powershell
python app.py
```

Mở trình duyệt: **http://localhost:5000**

---

## 🎯 Demo nhanh

### Đăng nhập với tài khoản demo
- **Admin**: `admin@fun.com` / `admin123`
- **User**: `user@fun.com` / `user123`

### Hoặc đăng ký tài khoản mới
1. Click "Đăng ký" trên trang chủ
2. Điền thông tin
3. Login và sử dụng AI models

---

## 🧠 Test AI Models

### MODEL 1: Dự đoán hóa đơn
**Input mẫu:**
```
Hóa đơn giày quận Sơn
Hóa đơn giày quận Tùng
Hóa đơn điện tử giấy quận Tùng
```

### MODEL 2: Nhận diện văn bản
- Upload bất kỳ ảnh nào có chứa văn bản
- Hệ thống sẽ nhận diện và trả về text

---

## 🔧 Troubleshooting

### Lỗi: "No module named 'flask'"
```powershell
pip install flask flask-login
```

### Lỗi: "Database not found"
```powershell
python create_database.py
```

### Port 5000 đang được sử dụng
Sửa trong `app.py`:
```python
app.run(debug=True, port=5001)
```

---

## 📂 File structure quan trọng

```
hackathon_project-main/
├── app.py                  ← Flask app chính
├── create_database.py      ← Tạo database
├── core/
│   ├── auth.py            ← Login logic
│   └── database.py        ← DB operations
└── ui/templates/
    ├── index.html         ← Landing page
    ├── signin.html        ← Login page
    ├── signup.html        ← Register page
    └── dashboard.html     ← AI Models dashboard ⭐
```

---

## 🎨 Screenshots

### Landing Page
![Landing](https://via.placeholder.com/800x400?text=Deep+Learning+System+Landing)

### Dashboard với 2 Models
![Dashboard](https://via.placeholder.com/800x400?text=AI+Models+Dashboard)

---

**Chúc bạn sử dụng vui vẻ! 🚀**
