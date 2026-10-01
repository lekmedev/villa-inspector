# Villa Inspector (Bảo trì villa) 📱🏖️

> Ứng dụng web di động phục vụ công tác kiểm tra, chụp ảnh "Trước" và "Sau" khi bảo trì/vệ sinh các căn Villa trong resort (1..80, trừ căn 13). Tự động nén ảnh, tải lên Google Drive theo cấu trúc thư mục quy chuẩn và ghi log Google Sheets qua Google Apps Script Web App.

- **URL Live:** [https://baotri.8biz.net](https://baotri.8biz.net)
- **Kiến trúc:** Web tĩnh (Single Page App) + Nginx Docker + Google Apps Script Backend (Serverless, Free).

---

## 🌟 Tính Năng Chính
1. **Thiết kế phong cách Apple iOS:**
   - Hỗ trợ Dark Mode (mặc định) & Light Mode.
   - Segmented Control trượt, Bottom Sheet Action, Dynamic Island Toast.
   - Mặc định focus vào tab **"Nay làm..."** để làm việc nhanh theo danh sách căn đã chọn điểm danh.
2. **Quản lý danh sách Villa thông minh:**
   - 79 căn villa (1..80, bỏ căn 13).
   - Đánh dấu sao ⭐ để chọn các căn muốn làm trong ca trực.
   - Tìm kiếm nhanh tức thì theo số hiệu căn.
   - Tự động di chuyển các căn đã đủ 2 ảnh (Trước/Sau) xuống mục **Đã hoàn thành** (Collapse / Thu gọn).
3. **Chụp ảnh & Tự động nén:**
   - Kích hoạt trực tiếp camera sau của điện thoại (`capture="environment"`).
   - Tự động nén ảnh bằng HTML5 Canvas (max 1280px, JPEG 70%) giúp tải nhanh, tiết kiệm 4G và tránh lỗi timeout của Google Apps Script.
   - Cho phép xem ảnh phóng to và chụp lại nếu cần.
4. **Lưu trữ & Đồng bộ:**
   - Lưu trạng thái và thumbnail vào `localStorage` của trình duyệt (không lo mất dữ liệu khi mất sóng).
   - Tự động gửi Base64 lên Google Apps Script để lưu trữ Google Drive & Google Sheets.

---

## 🛠️ Cấu Trúc Thư Mục & Bản Đồ Repo
```
.
├── AGENTS.md                  # Hướng dẫn chi tiết cho AI Coding Agent (kiến trúc, quy ước, cách mở rộng)
├── README.md                  # Tài liệu tổng quan dự án
├── docker-compose.yml         # File chạy container Nginx phục vụ web tĩnh
├── public/
│   ├── index.html             # Toàn bộ mã nguồn Single Page App (HTML, Tailwind CSS, JS)
│   ├── Code.gs.txt            # Mã nguồn Google Apps Script (Backend handler cho Drive & Sheets)
│   └── apple.html             # Bản demo giao diện phụ
```

---

## 🚀 Hướng Dẫn Cài Đặt & Triển Khai

### 1. Phía Google Apps Script (Backend)
1. Tạo thư mục trên Google Drive (lấy `PARENT_FOLDER_ID`).
2. Tạo Google Sheet mới (lấy `SPREADSHEET_ID`).
3. Mở [script.google.com](https://script.google.com) $\rightarrow$ Tạo New Project $\rightarrow$ Dán nội dung file `public/Code.gs.txt`.
4. Điền 2 ID tương ứng vào đầu file `Code.gs`.
5. Bấm **Deploy** $\rightarrow$ **New deployment** $\rightarrow$ Chọn loại **Web app**:
   - **Execute as:** `Me`
   - **Who has access:** `Anyone`
6. Copy Web App URL trả về.

### 2. Phía Web Frontend
- Mở web [https://baotri.8biz.net](https://baotri.8biz.net) $\rightarrow$ Bấm nút ⚙️ (Cài đặt) ở góc trên $\rightarrow$ Dán URL Google Apps Script $\rightarrow$ Lưu.

---

## 🐳 Triển Khai Với Docker (Self-hosted)
```bash
docker compose up -d
```
Container Nginx sẽ phục vụ thư mục `public/` tại port `127.0.0.1:8092`.
