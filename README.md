# Mock Todo Backend (Node.js & Express)

Một ứng dụng backend đơn giản sử dụng **Node.js** và **Express** cung cấp các API CRUD cơ bản để quản lý danh sách công việc (todos) với dữ liệu mock (in-memory). Dự án được thiết kế theo mô hình **MVC** (Model-View-Controller).

## Cấu trúc thư mục

```text
.
├── package.json
├── server.js               # File khởi chạy ứng dụng chính
└── src/
    ├── controllers/
    │   └── todoController.js # Xử lý logic nghiệp vụ và phản hồi HTTP
    ├── models/
    │   └── todoModel.js      # Lưu trữ và quản lý mock data
    └── routes/
        └── todoRoutes.js     # Khai báo các endpoints & routing
```

## Cài đặt & Khởi chạy

1. Cài đặt các thư viện phụ thuộc:
   ```bash
   npm install
   ```

2. Chạy server ở chế độ phát triển:
   ```bash
   npm start
   ```
   *Mặc định server sẽ khởi chạy tại cổng **3001** (`http://localhost:3001`).*

## API Endpoints (CRUD)

| Phương thức | Endpoint | Mô tả |
|---|---|---|
| `GET` | `/api/todos` | Lấy danh sách todos (Hỗ trợ lọc & tìm kiếm qua query parameters) |
| `GET` | `/api/todos/:id` | Lấy thông tin chi tiết của một todo |
| `POST` | `/api/todos` | Tạo mới một todo |
| `PUT` | `/api/todos/:id` | Cập nhật một todo |
| `DELETE` | `/api/todos/:id` | Xóa một todo |

### Tính năng Lọc & Tìm kiếm (`GET /api/todos`)
Bạn có thể truyền các tham số truy vấn sau trên URL:
- `q`: Tìm kiếm gần đúng (không phân biệt hoa/thường) theo tiêu đề của todo.
- `completed`: Lọc theo trạng thái hoàn thành (`true` hoặc `false`).

## Ví dụ sử dụng với `curl`

- **Lấy danh sách tất cả todos:**
  ```bash
  curl -s http://localhost:3001/api/todos
  ```

- **Tìm kiếm todo có chứa từ khoá "learn":**
  ```bash
  curl -s "http://localhost:3001/api/todos?q=learn"
  ```

- **Lọc các todo đã hoàn thành:**
  ```bash
  curl -s "http://localhost:3001/api/todos?completed=true"
  ```

- **Tạo mới todo:**
  ```bash
  curl -s -X POST -H "Content-Type: application/json" -d '{"title":"New Task"}' http://localhost:3001/api/todos
  ```

- **Cập nhật trạng thái todo:**
  ```bash
  curl -s -X PUT -H "Content-Type: application/json" -d '{"completed":true}' http://localhost:3001/api/todos/1
  ```

- **Xóa todo:**
  ```bash
  curl -s -X DELETE http://localhost:3001/api/todos/1
  ```
