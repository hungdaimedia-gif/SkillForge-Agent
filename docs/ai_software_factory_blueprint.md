# Hướng Dẫn & Kiến Trúc Xây Dựng AI Software Factory (Nhà Máy Phần Mềm AI)
> **Tài liệu tổng hợp dựa trên kiến trúc của Cole Medin (`coleam00`) và nền tảng Port (`getport.io`)**

---

## 1. Thông Tin Tác Giả & Các Kho Mã Nguồn Mở (GitHub Repositories)

Tác giả trong các video về AI Dark Factory & Agentic Engineering là **Cole Medin**.

- **Trang cá nhân GitHub:** [github.com/coleam00](https://github.com/coleam00)
- **Kênh YouTube:** [@ColeMedin](https://www.youtube.com/@ColeMedin)

### Danh sách các Repository cốt lõi:

| Repository | Mô tả & Vai trò trong hệ thống | Liên kết |
| :--- | :--- | :--- |
| **`ai-software-factory`** | **Kiến trúc nhà máy tối (Dark Factory):** Tự động hóa chu trình từ GitHub Issue $\rightarrow$ phân tích $\rightarrow$ lập trình $\rightarrow$ kiểm thử độc lập $\rightarrow$ mở Pull Request. Tích hợp trực tiếp với Port. | [coleam00/ai-software-factory](https://github.com/coleam00/ai-software-factory) |
| **`Archon`** | **Bộ khung điều phối (Harness Builder & Workflow Engine):** Công cụ lõi cho phép định nghĩa quy trình đa bước bằng YAML (Plan, Implement, Verify, Adversarial Review), chạy linh hoạt qua CLI, Web, GitHub Actions, Slack. | [coleam00/Archon](https://github.com/coleam00/Archon) |
| **`context-engineering-intro`** | **Context Engineering & Trí nhớ AI:** Kỹ thuật kiểm soát cửa sổ ngữ cảnh, tích hợp Second Brain / Knowledge Base tự tiến hóa theo phương pháp của Andrej Karpathy. | [coleam00/context-engineering-intro](https://github.com/coleam00/context-engineering-intro) |
| **`ai-transformation-workshop`** | **Tài liệu thực chiến & Git Worktrees:** Bộ câu lệnh, quy trình vòng lặp PIV (Plan - Implement - Verify) và cách chạy nhiều agent song song bằng Git Worktrees. | [coleam00/ai-transformation-workshop](https://github.com/coleam00/ai-transformation-workshop) |

---

## 2. Mô Hình Kiến Trúc 8 Khối (Port & Archon Blueprint)

```
                     ┌─────────────────────────────────────────┐
                     │          HUMAN IN THE LOOP              │
                     │  (Giao mục tiêu cấp cao & Nghiệm thu PR)│
                     └────────────────────┬────────────────────┘
                                          │
        ┌─────────────────────────────────┼─────────────────────────────────┐
        │                                 ▼                                 │
        │                 ┌───────────────────────────────┐                 │
        │                 │   ORCHESTRATION & DISPATCH    │                 │
        │                 │ (Archon Engine / Git Worktree │                 │
        │                 │  phân luồng song song)        │                 │
        │                 └───────────────┬───────────────┘                 │
        │                                 │                                 │
        ▼                                 ▼                                 ▼
┌──────────────┐                  ┌───────────────┐                 ┌──────────────┐
│ CONTEXT LAKE │ <--------------> │  AGENTS POOL  │ <-------------> │ SKILLS & MCP │
│              │                  │               │                 │              │
│ • Local Repo │                  │ • Claude Code │                 │ • FastMCP Hub│
│ • Rules / KIs│                  │ • Antigravity │                 │ • Skills Wiki│
│ • Karpathy   │                  │ • Tự Minh     │                 │ • Tools Run  │
│   Memory     │                  │ • Codex / Pi  │                 │              │
└──────────────┘                  └───────┬───────┘                 └──────────────┘
                                          │
                                          ▼
                          ┌───────────────────────────────┐
                          │     GOVERNANCE & EVAL GATES   │
                          │   (Cổng kiểm thử: Pytest,     │
                          │    Adversarial Multi-Agent)   │
                          └───────────────┬───────────────┘
                                          │
                                          ▼
                          ┌───────────────────────────────┐
                          │      METRICS & TELEMETRY      │
                          │ (Đo token, pass-rate, chi phí)│
                          └───────────────────────────────┘
```

### Chi tiết nhiệm vụ từng khối:

1. **Context Lake (Hồ ngữ cảnh):** Gom tài liệu dự án, quy tắc kiến trúc (`rules/`), kiến thức đã chắt lọc (`skills/`) vào cấu trúc tệp Markdown nhẹ, giúp Agent đọc trúng thông tin mà không gây phình to token.
2. **Skills Registry & MCP Hub (Kho kỹ năng):** Đóng gói mọi hành động (tạo ảnh, render video, truy vấn database, build dự án) thành các Tool chuẩn hóa qua giao thức FastMCP.
3. **Orchestration (Bộ điều phối Archon):** Nhận Issue, tạo nhánh Git Worktree độc lập cho từng Agent, giám sát tiến độ thực thi.
4. **Agents Pool (Đội ngũ Agent đa nhiệm):** Kết hợp nhiều mô hình (Anthropic Claude, Google Gemini, OpenAI, Meta Muse) cho đúng sở trường từng con.
5. **Governance & Eval Gates (Cổng kiểm duyệt chất lượng):** Quy tắc bất biến — *không tin tưởng code nếu chưa vượt qua kiểm thử tự động* (Pytest, Linting, hoặc cho 2 Agent tranh biện phản biện lẫn nhau).
6. **Human in the Loop:** Bạn chỉ xuất hiện ở 2 thời điểm: ra đầu bài ban đầu và bấm nút Merge PR khi mọi bài test đã xanh 100%.

---

## 3. Bản Đồ Ánh Xạ Vào Hệ Thống Hiện Tại Trên Máy Tính Của Bạn

Hệ thống của bạn đã sở hữu phần lớn hạ tầng cần thiết:

| Khối kiến trúc Cole Medin | Thành phần tương ứng trên máy tính của bạn | Trạng thái hiện tại |
| :--- | :--- | :--- |
| **Skills Registry** | `G:\SkillForge-Agent\skills_wiki\` | Đã có sẵn các skill (blender, graphics, media image/video). |
| **MCP Hub** | Antigravity MCP / FastMCP Servers | Đã tích hợp Everything, Screen, Premiere, CapCut, CLI. |
| **Worker Agent (Cloud)** | Meta Muse AI (Tự Minh) qua `muse` CLI | Đã thông suốt 100%, tự động nhận lệnh và trả code/media. |
| **Architect Agent (Local)** | Antigravity IDE (Gemini / Claude) | Đang kiểm duyệt, chạy test và trực tiếp quản lý Git. |
| **State Storage & VCS** | GitHub `hungdaimedia-gif` + Git local | Hoạt động ổn định trên nhánh `feat/knowledge-distill`. |

---

## 4. Lộ Trình Triển Khai Xây Dựng Thực Tế

### Giai đoạn 1: Chuẩn hóa Skills Registry với FastMCP
- Kết nối kho `skills_wiki` trong `G:\SkillForge-Agent` với server FastMCP runtime để mọi Agent nội bộ đều gọi dùng được các skill như một API thống nhất.

### Giai đoạn 2: Tự động hóa luồng Git Worktrees
- Thiết lập quy trình tự động: Mỗi khi có một task mới $\rightarrow$ tự tạo một Git Worktree riêng biệt để Agent viết code độc lập, không làm ảnh hưởng tới nhánh làm việc chính.

### Giai đoạn 3: Dựng Cổng Kiểm Thử Độc Lập (Adversarial Gate)
- Tạo kịch bản: Khi Agent 1 (ví dụ Tự Minh) nộp code, hệ thống tự động kích hoạt Agent 2 chạy test và phân tích bảo mật. Nếu kết quả đạt 100% test pass mới tự động tạo Pull Request cho bạn nghiệm thu.
