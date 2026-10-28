# 重現指南

## 歷史資料重算與離線範例

Python 3.10+，核心不需安裝套件。從專案根目錄執行 README 的五個指令。

`audit` 讀取 80 筆數值衍生檔，分開計算全部標籤與有文字子集。`terms` 讀取已彙整的歷史 POS 詞頻。`scrape` 與 `tfidf` 的預設文件範例使用合成輸入，不能與真實觀測合併。

```bash
PYTHONPATH=src python3 -m visionpro scrape --input tests/fixtures/news_synthetic.html --kind news --output output/news.json
PYTHONPATH=src python3 -m visionpro audit --output output/audit.json
diff results/historical_audit.json output/audit.json
PYTHONPATH=src python3 -m visionpro terms --output output/terms.json
diff results/historical_terms.json output/terms.json
python3 scripts/build_assets.py
python3 scripts/verify_project.py
```

`scripts/build_assets.py` 以公開快照重新製作兩張 SVG，不需要第三方套件。新撰寫 PDF 使用 `reportlab==4.4.9`，並內嵌本機中文字型子集；預設使用 macOS 的 Arial Unicode，可用 `VISIONPRO_REPORT_FONT` 指定另一個有繁體中文字的已授權 TrueType 字型。字型原檔未隨專案散布。PDF 生成程式會從公開衍生檔與已整理文字建立報告。原始 2023 PDF 不由本程式生成。

```bash
python3 -m pip install -r requirements-report.txt
python3 scripts/build_report.py
```

## 選用：單頁即時擷取

先確認擁有適當使用權限、網站規則與內文結構。以下是參數示意，`example.org` 不是歷史來源，並非可直接得到研究資料的指令：

```bash
PYTHONPATH=src python3 -m visionpro scrape --url https://example.org/article --allow-host example.org --kind news --output output/live.json
```

程式會檢查 HTTPS、明列的 host、robots.txt、回應類型、逾時與大小。每次只要求一頁，拒絕重新導向，不處理登入、年齡閘門或動態渲染。robots.txt 不可讀或不允許時停止。它不支援任意 PTT 鏡像的版型；請先以已授權保存的 HTML 檢查 selector，再做小範圍擷取。持續或批次作業應另實作頻率控制與完整記錄；此工具未提供批次爬取。

## 私人資料與模型驗證

公開衍生檔足以重算數字，但不含全文，所以不能從公開檔重新翻譯、重新分詞或評估情緒準確率。若持有原文，先核對 `text_sha256` 的 UTF-8 文字雜湊與來源，再另行標註；不要將私人快照放進公開專案。

原始服務設定未恢復，沒有「重跑即可得到同樣 Azure 分數」的承諾。新的模型輸出應存為另一個版本，保留語言、模型版本、日期與設定，並以人工真值評估。

