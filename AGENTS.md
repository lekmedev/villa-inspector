# AGENTS.md — Villa Inspector (Bảo Trì Villa)

Tài liệu này cung cấp toàn bộ bối cảnh hệ thống, kiến trúc, quy ước và luồng dữ liệu để AI Agent khi đọc lại repo có thể hiểu ngay mà không cần quét toàn bộ file hoặc suy luận từ đầu, giúp tiết kiệm tối đa token.

---

## 1. Bản Đồ Kho Chứa (Repository Map)
- **Vị trí trên máy chủ creek:** `/home/hermes/apps/baotri`
- **Tên container Docker:** `baotri-web` (chạy image `nginx:alpine`, port `127.0.0.1:8092 -> 80`, thuộc network `hermes-webui_default`).
- **Reverse Proxy:** Traefik tại `/home/hermes/apps/traefik/dynamic.yml` trỏ domain `baotri.8biz.net` về `http://baotri-web:80`.
- **Dashboard:** Đã đăng ký card vào `/home/hermes/apps/dashboard/services.json` (group Productivity Apps).

---

## 2. Kiến Trúc Kỹ Thuật (Architecture)
- **Frontend:** Single Page Application thuần (SPA) đặt tại `public/index.html`.
  - **Framework:** Không dùng React/Vue/Node.js build step; dùng HTML5 + Tailwind CSS qua CDN + Vanilla JavaScript.
  - **Phong cách UI:** Apple iOS Human Interface Guidelines (SF Pro text, Frosted Glass `backdrop-blur`, Segmented Control, Bottom Action Sheet, Pill Toasts).
  - **Theme:** Hỗ trợ Dark Mode (mặc định với class `dark` trên `<html>`) & Light Mode (lưu key `vi:theme` trong localStorage).
  - **Quy hoạch Villa:** Tổng 79 căn villa: mảng từ 1..80, **đã loại bỏ Villa 13** (`VILLAS_LIST`).

- **Xử lý ảnh & Client Pipeline:**
  - Kích hoạt Camera trực tiếp: `<input type="file" accept="image/*" capture="environment">`.
  - Nén ảnh: HTML5 Canvas `compressImage(file, maxWidth=1280, quality=0.7)` xuất ra Base64 JPEG.

- **Lưu trữ Cục Bộ (LocalStorage Keys):**
  - `vi:theme`: `'dark'` hoặc `'light'`.
  - `vi:favs`: Mảng số nguyên các căn được đánh dấu sao (ví dụ `[1, 3, 5, 7]`).
  - `vi:photos`: Object `{ [villaNum]: { before: "data:image/jpeg;base64,...", after: "..." } }`.
  - `vi:gas`: URL Web App Google Apps Script endpoint (doPost).

- **Backend (Serverless Google Apps Script):**
  - Mã nguồn: `public/Code.gs.txt`.
  - Endpoint: Nhận request `POST` JSON với payload:
    ```json
    {
      "villaId": "Villa 01",
      "type": "before" | "after",
      "image": "data:image/jpeg;base64,...",
      "mimeType": "image/jpeg"
    }
    ```
  - Logic GAS: Tạo/truy cập thư mục con `Villa_<villaId>` trong `PARENT_FOLDER_ID`, lưu ảnh tên `Villa_<villaId>_<type>_<timestamp>.jpg`, ghi URL & thời gian vào Google Sheet `SPREADSHEET_ID`.

---

## 3. Quy Ước Sửa Đổi & Mở Rộng Cho Agent
- **Khi thêm tính năng mới vào Web:** Chỉ chỉnh sửa trực tiếp `public/index.html`. Do Docker mount `- ./public:/usr/share/nginx/html:ro`, thay đổi có hiệu lực ngay lập tức mà không cần restart container.
- **Khi thêm/bớt số lượng Villa:** Điều chỉnh biến `TOTAL` và `VILLAS_LIST` ở đầu khối `<script>` trong `public/index.html`.
- **Khi cập nhật Google Apps Script:** Cập nhật đồng thời file `public/Code.gs.txt`.
