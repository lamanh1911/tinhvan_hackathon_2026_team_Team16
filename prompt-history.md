# Prompt History — tinhvan_hackathon_2026_team_Team16

**Sản phẩm:** AI Sales Follow-up Assistant (Relay)
**Repo:** https://github.com/lamanh1911/tinhvan_hackathon_2026_team_Team16
**Nguồn:** log session Claude Code (`cba25015-…jsonl`) — timestamp thật
**Khoảng thời gian:** 12/06/2026 14:53 → 13/06/2026 12:12 (giờ VN, UTC+7) — trong khung 24h
**Số prompt:** 34

> Ghi chú: cột **Level** là tự đánh giá theo rubric (L1=2đ: thiếu context; L2=5đ: có yêu cầu + công nghệ + output; L3=10đ: đủ Role/Context/Constraint/Expected Output). Reviewer có thể chấm lại.
> Loại hoạt động AI: **Phân tích yêu cầu · Thiết kế/Kiến trúc · Sinh code · Test/Debug · Viết tài liệu**.

| # | Thời gian (VN) | Prompt | Hoạt động AI | Đối chiếu sản phẩm | Level |
|---|---|---|---|---|---|
| 1 | 12/06 14:53:55 | ok, tôi đã add key openrouter vào .env rồi, giờ thử fake 1 file txt transcript giúp tôi | Test/Debug · Sinh code | FR-05 MOM — test LLM thật | L2 |
| 2 | 12/06 15:51:20 | có phải reload server hay gì ko, hay access http://localhost:3000/meetings là đc | Test/Debug | Chạy local | L1 |
| 3 | 12/06 15:56:07 | có vẻ như là đã call được AI API rồi, nhưng câu prompt hiện tại là gì để summarize vậy? có chỉnh để cho chi tiết hơn được không | Phân tích yêu cầu | Prompt tóm tắt MOM (llm_client) | L2 |
| 4 | 12/06 15:58:56 | phần next action có phải tự generate từ AI tóm tắt không? Hay là đang hardcode | Phân tích yêu cầu | FR-05 next_actions | L2 |
| 5 | 12/06 16:04:59 | Ok phần code đã xong, thực hiện tạo nhánh mới và commit code lên đó, nhớ checkout về nhánh chính và pull code mới nhất | Sinh code | Git workflow Sprint 5 | L2 |
| 6 | 12/06 16:19:12 | ok, sau đó tạo giúp tôi compare request, tôi sẽ review code và tạo pull request bằng tay | Sinh code | PR Sprint 5 | L2 |
| 7 | 12/06 16:22:10 | tôi cần tổng hợp các câu prompt tôi từng chat với bạn trong session này, có thể list ra một file txt giúp tôi được không | Viết tài liệu | Export prompt history | L2 |
| 8 | 13/06 09:38:39 | tôi muốn tìm hiểu nghiệp vụ của sprint 2 và sprint 3, có thể kiểm tra và tóm tắt lại giúp tôi được ko | Phân tích yêu cầu | FR-01 Card, FR-02 Thank-you | L2 |
| 9 | 13/06 09:42:18 | Tôi muốn pull code mới nhất trên github về, hãy giúp tôi pull code | Test/Debug | Sync repo (main) | L1 |
| 10 | 13/06 09:46:33 | Giờ hãy run local cho tôi | Test/Debug | Chạy local toàn stack | L1 |
| 11 | 13/06 10:02:17 | Ok hiện tại tôi muốn làm tiếp tính năng card, đã lấy được thông tin khách hàng sau khi đọc namecard thì tiếp nghiệp vụ sẽ là gì | Phân tích yêu cầu | FR-01 → FR-02 (nghiệp vụ) | L2 |
| 12 | 13/06 10:05:57 | Phương án 2, Đọc từ calendar qua Microsoft Graph (cần Azure credentials) thì tôi cần làm gì? | Thiết kế/Kiến trúc | FR-02 + MS Graph | L2 |
| 13 | 13/06 10:19:00 | okay, hold on phần tính năng này, bắt đầu thực hiện việc deploy lên railway, có CI/CD với github repo, tôi cần làm gì | Thiết kế/Kiến trúc | Deploy Railway + CI/CD | L2 |
| 14 | 13/06 10:26:21 | hold on, hiện tại project này đang được link remote tới 1 repo khác, tôi muốn add thêm remote hoặc đổi remote sang 1 repo trống... (repo lamanh1911) | Thiết kế/Kiến trúc · Sinh code | Git remote / deploy source | L2 |
| 15 | 13/06 10:35:02 | nếu tôi link account github trước mới tạo database được không? không thấy mục tạo database | Test/Debug | Railway — tạo Postgres | L1 |
| 16 | 13/06 10:39:12 | railway đang thực hiện build, sau đó sẽ cần tạo service manually đúng ko *(kèm ảnh)* | Test/Debug | Railway services | L1 |
| 17 | 13/06 10:44:07 | okay, tôi đã tạo thêm database, what's next *(kèm ảnh)* | Test/Debug | Railway Postgres | L1 |
| 18 | 13/06 10:46:05 | *(dán log Railway)* image push 421.8MB → Healthcheck `/health` failed | Test/Debug | Backend deploy — healthcheck | L1 |
| 19 | 13/06 10:48:44 | database url co phai giong nhu local: postgresql://postgres@localhost:5432/relay khong | Test/Debug | DATABASE_URL (Railway) | L1 |
| 20 | 13/06 10:52:36 | ok, them bien database, secret_key, openrouter api cho backend roi, sao nua | Test/Debug | Backend env vars | L1 |
| 21 | 13/06 10:55:20 | oki, gio thi backend online, database online, what's next | Test/Debug | Tiến độ deploy | L1 |
| 22 | 13/06 10:56:59 | …railway.app/ generate domain đây, not found | Test/Debug | Backend domain (/health) | L1 |
| 23 | 13/06 11:00:28 | sau khi chọn source src/components và chuyển sang generate domain, màn hình hiện như này *(kèm ảnh)* | Test/Debug | Frontend service domain | L1 |
| 24 | 13/06 11:02:23 | đây là lỗi khi deploy src/components *(kèm ảnh)* | Test/Debug | Frontend build — Next.js vuln | L1 |
| 25 | 13/06 11:10:54 | health check issues *(kèm ảnh)* | Test/Debug | Frontend healthcheck | L1 |
| 26 | 13/06 11:15:08 | ok online hết rồi, what's next | Test/Debug | Tiến độ deploy | L1 |
| 27 | 13/06 11:18:24 | có vẻ như vẫn nhận port 8000 *(kèm ảnh)* | Test/Debug | NEXT_PUBLIC_API_BASE_URL / CORS | L1 |
| 28 | 13/06 11:26:18 | Đã deploy thành công, giờ quay lại bài toán của sprint 2 và sprint 3 | Phân tích yêu cầu | FR-01 / FR-02 | L1 |
| 29 | 13/06 11:33:59 | Duyệt ý tưởng, OK hãy lên kế hoạch chi tiết cho tôi | Thiết kế/Kiến trúc | Plan tính năng Thank-you | L1 |
| 30 | 13/06 11:51:11 | Thôi tôi không cần thực hiện nữa, dừng update tính năng. Tôi muốn export lịch sử prompt ra file txt | Viết tài liệu | Export prompt history | L2 |
| 31 | 13/06 11:59:36 | Tôi muốn đổi tên Repository theo cấu trúc tinhvan_hackathon_2026_team_Team16, việc đổi tên như này có ảnh hưởng đến cấu hình deploy trên railway ko | Phân tích yêu cầu | Repo rename ↔ Railway | L2 |
| 32 | 13/06 12:04:52 | okay, tôi đã đổi tên repo thành tinhvan_hackathon_2026_team_Team16 | Test/Debug | Git remote update | L1 |
| 33 | 13/06 12:06:50 | Tôi cần export lại prompt history dựa theo những tiêu chí trong ảnh, hãy chỉ cho tôi những hạng mục có thể export ra *(kèm ảnh)* | Viết tài liệu | Prompt history (rubric) | L2 |
| 34 | 13/06 12:12:48 | định dạng MD, chỉ timestamp từ 14:00 VNT ngày 12/06/2026 | Viết tài liệu | Prompt history export | L2 |

---

## Thống kê nhanh

- **Phân tích yêu cầu:** prompt 3, 4, 8, 11, 28, 31
- **Thiết kế/Kiến trúc:** prompt 12, 13, 14, 29
- **Sinh code:** prompt 1, 5, 6, 14
- **Test/Debug:** prompt 1, 2, 9, 10, 15–27, 32 (chủ yếu giai đoạn deploy Railway)
- **Viết tài liệu:** prompt 7, 30, 33, 34

**Dòng thời gian chính:**
1. Test AI thật (OpenRouter) cho FR-05 MOM — chiều 12/06
2. Git: tạo nhánh, commit, PR Sprint 5 — chiều 12/06
3. Pull code mới + run local toàn stack — sáng 13/06
4. Phân tích nghiệp vụ FR-01 → FR-02 — sáng 13/06
5. Deploy Railway + CI/CD (backend, Postgres, frontend, fix Next vuln / healthcheck / CORS) — 13/06
6. Đổi tên repo + export prompt history — trưa 13/06
