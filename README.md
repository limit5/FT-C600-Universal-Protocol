# FT-C600 Universal Protocol (FUP)

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20ARM64-lightgrey)
![Language](https://img.shields.io/badge/language-C%2B%2B%20%7C%20Python%20%7C%20TypeScript-green)
![AI-Ready](https://img.shields.io/badge/AI_Agent-Ready-blueviolet)

FT-C600 Universal Protocol (FUP) 是專為 FT-C600 (Cortex-A7) 影像掃描平台打造的**通用通訊協議中樞**。

本倉庫採用 **單一真理來源 (Single Source of Truth, SSOT)** 架構，將「抽象數據定義」與「物理傳輸層」徹底解耦。無論是透過 USB (UVC XU) 傳輸，或是透過網路 (RTSP/ONVIF CGI) 控制，所有的通訊代碼皆由本倉庫自動生成，確保跨平台、跨團隊的通訊邏輯 100% 同步。

---

## 🎯 支援生態系 (Supported Ecosystems)

本倉庫的自動化生成工具支援以下專案無縫對接：

* **Embedded Linux SDK**: 提供符合硬體快取對齊、精準 60-byte 長度的 C 結構體，供韌體層直接掛載。
* **UVCCamera (MFC)**: 提供 Windows x64 下具備 `pragma pack(1)` 與 Little-Endian 轉換的 C++ 定義。
* **Qt 6.8 跨平台 App**: 透過 CMake 自動整合，提供具備 Qt JSON 序列化能力的網路模型與 UVC 二進位模型。
* **OmniSight-Forge**: 為 React/Node.js 前端提供強型別的 TypeScript Interfaces。
* **gi5_sim 分析工具**: 讓 Python 演算法開發者能精確解包 UVC 二進位流或解析 RTSP JSON 參數。

---

## 📂 完整目錄結構與說明 (Architecture)

本倉庫嚴格區分「定義 (What)」與「傳輸 (How)」，並為各平台提供豐富的範例。

~~~text
FT-C600-UNIVERSAL-PROTOCOL/
├── definitions/               # 【核心定義層】中立的資料結構 (SSOT)
│   ├── barcode.json           # 條碼掃描與解碼結果
│   ├── file_transfer.json     # 大檔/字串分塊傳輸
│   ├── imaging.json           # AE 狀態與 GI v5 引擎參數
│   └── system.json            # 系統狀態、版本與安全握手
├── transports/                # 【物理傳輸層】定義數據如何發送
│   ├── cpp/                   # C++ 共享編譯邏輯 (CMake 與端序轉換)
│   ├── rtsp_onvif/            # 網路傳輸專用：HTTP/CGI 端點映射
│   └── uvc_xu/                # USB 傳輸專用：60-byte 二進位 ID 映射
├── generators/                # 【自動化工具層】Python 核心生成腳本
├── tests/                     # 【品質保證層】JSON 結構與硬體限制單元測試
├── examples/                  # 【開發者範例】各平台如何調用生成的代碼
│   ├── cpp_qt_app/            # Qt 6.8 雙模通訊範例 (USB & Wi-Fi 切換)
│   ├── cpp_mfc_app/           # Windows MFC XU 與網路請求雙模範例
│   ├── python_gi5_sim/        # Python 二進位解包與 JSON 解析範例
│   └── ts_react_frontend/     # React 前端強型別 API 呼叫範例
├── dist/                      # 【產出分發層】腳本自動生成的代碼 (切勿手動修改)
│   ├── c/                     # (自動生成) C 結構體
│   ├── cpp_qt/                # (自動生成) Qt 模型與二進位結構
│   └── ts/                    # (自動生成) TypeScript 介面
├── .github/                   # GitHub CI/CD 與 Copilot 設定
├── docs/                      # 硬體規格文件
├── llms.txt                   # 🤖 AI 協作最高指導原則
├── CLAUDE.md                  # 指向 llms.txt 的軟連結 (給 Claude)
├── .cursorrules               # 指向 llms.txt 的軟連結 (給 Cursor)
├── .editorconfig              # 統一編輯器排版規範
├── .gitignore                 # 排除編譯暫存檔
└── README.md                  # 專案首頁
~~~

---

## 🚀 快速上手 (Getting Started)

### 1. 開發環境需求
建議在 WSL2 (Ubuntu) 或 Windows 終端機下執行：
* **Python 3.8+** (用於執行生成器與單元測試)
* **CMake 3.16+** (若需要整合至 Qt/C++ 專案)

### 2. 新增或修改協議 (SOP)
**切勿手動修改 `dist/` 下的任何代碼！** 所有修改必須遵循以下流程：

1. 修改 `definitions/` 下的 JSON 檔案。
2. 若有新增指令，更新 `transports/*/mapping.json`。
3. 執行單元測試以確保硬體限制未被打破：
   ~~~bash
   python3 -m unittest tests/test_definitions.py -v
   ~~~
4. 測試通過後，執行代碼生成：
   ~~~bash
   # 產出所有平台代碼 (Qt C++, C SDK, TypeScript)
   python3 generators/gen_protocol.py --mode all
   ~~~

---

## 🤖 AI 多代理協作規範 (AI Collaboration)

本專案高度依賴自動化生成腳本。為防止 AI 代理（如 Cursor, Claude Code, GitHub Copilot 等）產生幻覺並誤改生成代碼，本倉庫採用了統一的 AI 指令規範。

**請勿讓 AI 直接修改 `dist/` 目錄。** 若要讓 AI 協助修改協議，請遵循以下設定，將專案根目錄的 `llms.txt` 注入至您的 AI 工具中：

~~~bash
# 1. 確保根目錄存在 llms.txt (給一般網頁爬蟲與標準 LLM 讀取)

# 2. 讓 Cursor IDE 遵循規範
ln -s llms.txt .cursorrules

# 3. 讓 Claude Code (CLI) 遵循規範
ln -s llms.txt CLAUDE.md

# 4. 讓 GitHub Copilot 遵循規範
mkdir -p .github && ln -s ../llms.txt .github/copilot-instructions.md
~~~

⚠️ **AI 協作鐵則：**
在讓任何具有執行權限的 AI 代理執行跨檔案修改或自動化腳本前，**務必確保 `git status` 是乾淨的 (已 Commit)**，以防範 AI「幻覺雪崩」破壞專案架構。

---

## 🗺️ 發展藍圖 (Roadmap)
* [x] **v1.0**: 建立 UVC XU 核心通訊與 60-byte 限制檢查。
* [x] **v2.0**: 引入自動化生成工具、多框架支援 (Qt/MFC/React/Python) 與單元測試。
* [x] **v2.1**: 實作 AI 代理協作規範 (`llms.txt`) 與 `examples/` 雙軌範例庫。
* [ ] **v3.0**: 擴充 `rtsp_onvif` 傳輸層，支援完整 ONVIF Profile M Metadata 串流與 JSON CGI API。

---

## 📄 授權條款 (License)
本專案採用 [MIT License](LICENSE) 授權。詳細資訊請參閱 LICENSE 檔案。