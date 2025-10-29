# 👑 Admin User Management - Hướng dẫn sử dụng

## ✨ Tính năng mới đã thêm

### 🎯 **Admin Dashboard = User Dashboard + Quản lý User**

Admin khi đăng nhập sẽ thấy:
- ✅ **Giao diện giống User** - Có đầy đủ 2 AI Models
- ✅ **Badge "ADMIN"** màu đỏ bên cạnh tên
- ✅ **Nút "Quản lý User"** màu xanh lá

---

## 🚀 Cách sử dụng

### 1. Đăng nhập với tài khoản Admin
```
Email: admin@fun.com
Password: admin123
```

### 2. Mở Panel Quản lý User
- Click nút **"Quản lý User"** (màu xanh lá) ở góc trên bên phải
- Hoặc nhấn phím **ESC** để đóng panel

### 3. Xem thống kê
Panel hiển thị 3 thẻ thống kê:
- 📊 **Tổng người dùng** (màu tím)
- ✅ **Người dùng hoạt động** (màu xanh)
- 👑 **Quản trị viên** (màu cam)

### 4. Quản lý người dùng
#### 🔍 **Tìm kiếm**
- Gõ vào ô tìm kiếm để lọc theo:
  - Tên người dùng
  - Email
  - Vai trò

#### ✏️ **Sửa vai trò**
- Click nút **"Sửa"** (màu xanh dương)
- Xác nhận thay đổi
- Vai trò sẽ chuyển đổi: `admin` ⟷ `user`

#### 🗑️ **Xóa người dùng**
- Click nút **"Xóa"** (màu đỏ)
- Xác nhận cảnh báo (⚠️ **KHÔNG THỂ HOÀN TÁC**)
- User bị xóa khỏi hệ thống

---

## 🎨 Giao diện Panel

```
┌─────────────────────────────────────────┐
│  👑 Quản lý người dùng            [X]   │
├─────────────────────────────────────────┤
│  ┌─────┐  ┌─────┐  ┌─────┐            │
│  │  5  │  │  4  │  │  1  │   ← Stats  │
│  │Total│  │Active│ │Admin│            │
│  └─────┘  └─────┘  └─────┘            │
│                                         │
│  📋 Danh sách người dùng   🔍 Search   │
│  ┌───────────────────────────────────┐ │
│  │ Người dùng │ Email │ Role │ Date │ │
│  ├───────────────────────────────────┤ │
│  │ 👤 Admin   │...    │ 👑   │ ... │ │
│  │ 👤 User 1  │...    │ 👤   │ ... │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

---

## 🔐 Phân quyền

### Admin có thể:
- ✅ Sử dụng 2 AI Models (MODEL 1 & MODEL 2)
- ✅ Xem danh sách tất cả người dùng
- ✅ Thay đổi vai trò user ⟷ admin
- ✅ Xóa người dùng
- ✅ Tìm kiếm và lọc người dùng

### User thường chỉ:
- ✅ Sử dụng 2 AI Models
- ❌ Không thấy nút "Quản lý User"
- ❌ Không truy cập được admin panel

---

## 💡 Tính năng nổi bật

### 1. **Real-time Search**
- Tìm kiếm không cần reload
- Filter theo nhiều tiêu chí
- Kết quả ngay lập tức

### 2. **Beautiful UI/UX**
```css
✨ Gradient backgrounds
🎨 Smooth animations
📱 Responsive design
🌓 Dark overlay với backdrop blur
```

### 3. **User-friendly**
- Click ngoài panel → đóng panel
- Phím ESC → đóng panel
- Confirm trước khi xóa
- Badge màu sắc phân biệt role

### 4. **Stats Cards**
- Auto update khi thay đổi
- Gradient colors eye-catching
- Icons rõ ràng

---

## 🛠️ Technical Details

### API Endpoint
```
GET /api/admin/users
Authorization: Admin only
Response: JSON array of users
```

### Database Schema
```sql
users (
  id INTEGER PRIMARY KEY,
  email TEXT,
  first_name TEXT,
  last_name TEXT,
  role TEXT,  -- 'admin' or 'user'
  created_at TIMESTAMP
)
```

---

## 📸 Screenshots

### Dashboard cho Admin
```
┌──────────────────────────────────────────────┐
│ 🧠 Deep Learning Models Dashboard           │
│                              [👤 Ngoc ADMIN] │
│                              [Quản lý User]  │
│                              [Logout]        │
├──────────────────────────────────────────────┤
│  ┌───────────┐  ┌───────────┐               │
│  │  MODEL 1  │  │  MODEL 2  │               │
│  │  📄→📊   │  │  🖼️→📝   │               │
│  └───────────┘  └───────────┘               │
└──────────────────────────────────────────────┘
```

### Dashboard cho User
```
┌──────────────────────────────────────────────┐
│ 🧠 Deep Learning Models Dashboard           │
│                              [👤 User Name]  │
│                              [Logout]        │
├──────────────────────────────────────────────┤
│  ┌───────────┐  ┌───────────┐               │
│  │  MODEL 1  │  │  MODEL 2  │               │
│  │  📄→📊   │  │  🖼️→📝   │               │
│  └───────────┘  └───────────┘               │
└──────────────────────────────────────────────┘
```

---

## 🎯 Testing

### Test Admin Login:
1. Go to http://localhost:5000
2. Login: `admin@fun.com` / `admin123`
3. ✅ Thấy badge "ADMIN" màu đỏ
4. ✅ Thấy nút "Quản lý User" màu xanh
5. Click "Quản lý User"
6. ✅ Panel hiện lên với danh sách users

### Test User Login:
1. Login: `user@fun.com` / `user123`
2. ✅ Không thấy badge ADMIN
3. ✅ Không thấy nút "Quản lý User"
4. ✅ Chỉ dùng được AI models

---

## 🚀 Future Enhancements

- [ ] Export user list to CSV/Excel
- [ ] Bulk operations (xóa nhiều users)
- [ ] User activity logs
- [ ] Email invitation system
- [ ] Advanced filtering (by role, date range)
- [ ] Pagination for large user lists
- [ ] Real-time updates with WebSocket

---

**Happy Managing! 👑**
