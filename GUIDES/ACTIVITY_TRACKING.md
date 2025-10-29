# 📈 Hướng Dẫn Theo Dõi Hoạt Động Người Dùng

## Tổng Quan

Hệ thống theo dõi hoạt động cho phép Admin giám sát cách người dùng tương tác với ứng dụng Deep Learning, bao gồm:
- 🔐 Số lần đăng nhập
- 🤖 Số lần sử dụng MODEL1 (dự đoán hóa đơn)
- 🖼️ Số lần sử dụng MODEL2 (nhận diện văn bản)
- ⏰ Thời gian truy cập cuối cùng
- 🟢 Trạng thái online/offline

## Cấu Trúc Database

### Bảng `user_activity`

```sql
CREATE TABLE user_activity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    login_count INTEGER DEFAULT 0,
    model1_usage INTEGER DEFAULT 0,
    model2_usage INTEGER DEFAULT 0,
    last_access TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
```

### Indexes
- `idx_user_activity_user_id`: Tăng tốc truy vấn theo user_id
- `idx_user_activity_last_access`: Tăng tốc sắp xếp theo thời gian

## Cách Hoạt Động

### 1. Tracking Login
Khi user đăng nhập thành công:
```python
# Trong route /auth/signin
track_user_activity(user_data['id'], 'login')
# → Tăng login_count + 1
# → Cập nhật last_access = CURRENT_TIMESTAMP
```

### 2. Tracking MODEL1 Usage
Khi user sử dụng MODEL1:
```python
# Trong route /api/model1/predict
track_user_activity(current_user.id, 'model1')
# → Tăng model1_usage + 1
# → Cập nhật last_access = CURRENT_TIMESTAMP
```

### 3. Tracking MODEL2 Usage
Khi user sử dụng MODEL2:
```python
# Trong route /api/model2/recognize
track_user_activity(current_user.id, 'model2')
# → Tăng model2_usage + 1
# → Cập nhật last_access = CURRENT_TIMESTAMP
```

## Giao Diện Admin

### Truy Cập Bảng Activity

1. **Đăng nhập với tài khoản Admin**
   ```
   Email: admin@admin.com
   Password: admin123
   ```

2. **Click nút "Quản lý User"** (góc trên bên phải)

3. **Chuyển sang tab "Hoạt Động"** trong panel quản lý

### Tính Năng Bảng Activity

#### Cột Hiển Thị
| Cột | Mô Tả | Ví Dụ |
|-----|-------|-------|
| **User** | Họ tên người dùng | Nguyễn Văn A |
| **Email** | Địa chỉ email | user@test.com |
| **Đăng Nhập** | Số lần login | 15 lần |
| **MODEL1** | Số lần dùng MODEL1 | 23 lần |
| **MODEL2** | Số lần dùng MODEL2 | 8 lần |
| **Truy Cập Cuối** | Thời gian gần nhất | 2 phút trước |
| **Trạng Thái** | Online/Offline | 🟢 Online |

#### Màu Sắc Activity Count
- **🔴 Cao (≥10)**: Badge màu đỏ - User rất hoạt động
- **🟡 Trung bình (5-9)**: Badge màu vàng - User hoạt động vừa phải
- **🟢 Thấp (0-4)**: Badge màu xanh - User ít hoạt động

#### Trạng Thái Online
- **🟢 Online**: User truy cập trong vòng 5 phút gần đây (có hiệu ứng pulse)
- **⚫ Offline**: User không hoạt động quá 5 phút

### Bộ Lọc Thời Gian

Lọc dữ liệu theo khoảng thời gian:
- **Hôm nay**: Hoạt động trong ngày hôm nay
- **Tuần này**: Hoạt động trong 7 ngày gần đây
- **Tháng này**: Hoạt động trong 30 ngày gần đây

```javascript
// Dropdown filter
<select onchange="filterActivity()">
    <option value="all">Tất cả</option>
    <option value="today">Hôm nay</option>
    <option value="week">Tuần này</option>
    <option value="month">Tháng này</option>
</select>
```

### Làm Mới Dữ Liệu

Click nút "🔄 Làm mới" để reload dữ liệu mới nhất từ server.

## API Endpoints

### GET `/api/admin/activity`

**Mô tả**: Lấy dữ liệu hoạt động của tất cả users

**Authorization**: Chỉ Admin (role='admin')

**Response**:
```json
[
  {
    "id": 1,
    "email": "user@test.com",
    "first_name": "Test",
    "last_name": "User",
    "role": "user",
    "login_count": 15,
    "model1_usage": 23,
    "model2_usage": 8,
    "last_access": "2025-01-20 14:35:22"
  },
  ...
]
```

**Error Response** (Non-admin):
```json
{
  "success": false,
  "message": "Unauthorized"
}
```
Status Code: `403 Forbidden`

## Ví Dụ Sử Dụng

### Kiểm Tra User Nào Hoạt Động Nhiều Nhất

1. Login với admin@admin.com
2. Click "Quản lý User" → Tab "Hoạt động"
3. Quan sát cột "MODEL1" và "MODEL2"
4. Users có badge đỏ (≥10) là người dùng tích cực

### Phát Hiện User Không Hoạt Động

1. Lọc theo "Tháng này"
2. Tìm users có:
   - Login count = 0 hoặc thấp
   - MODEL1/MODEL2 usage = 0
   - Trạng thái Offline
3. Xem xét gửi email nhắc nhở hoặc xóa tài khoản

### Monitor Real-time Activity

1. Mở bảng Activity
2. Click "🔄 Làm mới" định kỳ (mỗi 30s-1 phút)
3. Quan sát:
   - Trạng thái Online/Offline thay đổi
   - Số lần sử dụng model tăng lên
   - Last access time cập nhật

## Troubleshooting

### ❌ Bảng activity không hiển thị dữ liệu

**Nguyên nhân**: Database chưa có bảng `user_activity`

**Giải pháp**:
```bash
python create_database.py
# hoặc
python add_activity_tracking.py
```

### ❌ Activity count không tăng

**Nguyên nhân**: Hàm `track_user_activity()` không được gọi

**Kiểm tra**:
1. Xem logs trong terminal Flask
2. Đảm bảo routes có gọi `track_user_activity()`
3. Kiểm tra database có insert/update được không

### ❌ Trạng thái Online luôn là Offline

**Nguyên nhân**: Thời gian server không đồng bộ hoặc logic isUserOnline() sai

**Giải pháp**:
```javascript
// Tăng thời gian timeout từ 5 phút lên 10 phút
function isUserOnline(lastAccess) {
    const now = new Date();
    const lastTime = new Date(lastAccess);
    return (now - lastTime) < 10 * 60 * 1000; // 10 minutes
}
```

## Mở Rộng Trong Tương Lai

### 1. Export Dữ Liệu
Thêm nút export CSV/Excel:
```javascript
function exportActivityToCSV() {
    // Convert activityData to CSV format
    // Trigger download
}
```

### 2. Biểu Đồ Thống Kê
Sử dụng Chart.js để hiển thị:
- Biểu đồ cột: Số lần login theo ngày
- Biểu đồ tròn: Tỷ lệ sử dụng MODEL1 vs MODEL2
- Biểu đồ đường: Xu hướng hoạt động theo thời gian

### 3. Real-time với WebSocket
Tự động cập nhật mà không cần click "Làm mới":
```javascript
const socket = io();
socket.on('activity_update', (data) => {
    renderActivityTable(data);
});
```

### 4. Thông Báo Push
Gửi thông báo khi:
- User mới đăng ký
- Hoạt động bất thường (quá nhiều requests)
- User VIP online

## Bảo Mật

⚠️ **Quan trọng**:
- Chỉ Admin mới truy cập được `/api/admin/activity`
- Middleware kiểm tra role='admin' trước khi trả dữ liệu
- Không hiển thị password hoặc thông tin nhạy cảm
- Log tất cả các hành động admin để audit trail

## Kết Luận

Hệ thống theo dõi hoạt động giúp Admin:
- ✅ Hiểu rõ hành vi người dùng
- ✅ Tối ưu hóa tài nguyên hệ thống
- ✅ Phát hiện anomaly và spam
- ✅ Đưa ra quyết định về UX/UI dựa trên data

Nếu có thắc mắc, liên hệ với team phát triển! 🚀
