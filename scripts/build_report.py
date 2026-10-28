"""Create the new public case-study PDF, separate from the original 2023 report."""
import json
import os
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab import rl_config
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Flowable

ROOT=Path(__file__).resolve().parents[1]
AUDIT=json.loads((ROOT/'results/historical_audit.json').read_text())
font_path=Path(os.environ.get('VISIONPRO_REPORT_FONT','/System/Library/Fonts/Supplemental/Arial Unicode.ttf'))
if not font_path.exists():
    raise SystemExit('Set VISIONPRO_REPORT_FONT to a locally licensed TrueType font containing Traditional Chinese glyphs.')
pdfmetrics.registerFont(TTFont('ReportCJK',str(font_path)))
rl_config.invariant=1
INK=colors.HexColor('#17334b')
TEAL=colors.HexColor('#167b67')
BODY=ParagraphStyle('body',fontName='ReportCJK',fontSize=11,leading=18,textColor=INK,wordWrap='CJK',spaceAfter=13)
SMALL=ParagraphStyle('small',parent=BODY,fontSize=9,leading=14,spaceAfter=8)
H2=ParagraphStyle('h2',parent=BODY,fontSize=15,leading=22,textColor=TEAL,spaceBefore=14,spaceAfter=9)
TITLE=ParagraphStyle('title',fontName='Helvetica-Bold',fontSize=29,leading=34,textColor=INK,spaceAfter=15)
story=[]

def p(text,style=BODY):
    story.append(Paragraph(text,style))

def heading(kicker,title):
    p(kicker,ParagraphStyle('k',fontName='Helvetica',fontSize=10,leading=14,textColor=TEAL,spaceAfter=13))
    p(title,TITLE)

def table(rows,widths):
    content=[[Paragraph(str(cell),SMALL) for cell in row] for row in rows]
    t=Table(content,colWidths=widths,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e5f0f2')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.7,TEAL),('LINEBELOW',(0,1),(-1,-1),.3,colors.HexColor('#d3dfe6')),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
    story.extend([t,Spacer(1,12)])

class Bars(Flowable):
    def __init__(self):
        super().__init__();self.width=483;self.height=145
    def draw(self):
        c=self.canv
        for y,key,label in [(108,'all_stored_labels','All stored labels / n=80'),(40,'text_present_only','Text retained / n=72')]:
            c.setFont('Helvetica',10);c.setFillColor(INK);c.drawString(0,y+22,label)
            x=0
            for category,color in [('positive','#167b67'),('neutral','#91a5b8'),('negative','#db765e')]:
                percent=AUDIT[key]['percent'][category];width=483*percent/100
                c.setFillColor(colors.HexColor(color));c.rect(x,y-6,width,22,fill=1,stroke=0)
                c.setFont('Helvetica-Bold',9);c.setFillColor(colors.white);c.drawCentredString(x+width/2,y+1,f'{percent:.2f}%');x+=width
        c.setFont('Helvetica',9);c.setFillColor(INK);c.drawString(0,4,'Positive / Neutral / Negative | Historical predictions, not human ground truth')

heading('01 / RESEARCH PURPOSE','Vision Pro Social Listening')
p('從網路輿情到產品定位：網路資料蒐集、文字探勘與情緒分析',H2)
p('作者：李奕成 Eason<br/>國立成功大學 Information Management<br/>原始研究：2023 年｜專案整理與資料重算：2026-10-28',BODY)
p('學號：公開版本省略；原始署名報告與完整研究資料留存於本機私人封存。',SMALL)
p('研究目的',H2)
p('2023 年生成式 AI 成為科技討論焦點時，Apple 發表 Vision Pro，使 AR、MR 與空間運算再次進入產品策略討論。本研究想理解：對技術的期待，是否也代表購買意願？價格、產品用途與內容生態系又如何影響外界對產品的定位？')
p('我選擇這個題目，是因為創新產品的規格與市場接受度未必同步。網路文字能提供早期的問題線索，但若只看整體正負比例，也可能忽略價格疑慮、使用情境與語意誤判。')
p('專案摘要',H2)
table([['研究材料','可檢查的成果'],['八個媒體、部落格及論壇來源項目','原始蒐集 81 個片段；歷史儲存 80 個情緒標籤'],['Azure 歷史輸出與中文詞性中間資料','保留文字 72 筆；8 筆空白仍有正面標籤'],['2026 年公開專案整理','逐筆資料品質重算、來源修復、Python 擷取與詞權重範例']], [178,305])
p('這是一份歷史研究的公開個案整理。原始 11 頁 PDF 保持不變；本文件重新說明研究流程、重算結果、限制與產業用途。',SMALL)
story.append(PageBreak())

heading('02 / DATA AND METHODS','From Web Text to Evidence')
p('資料來源與分析單位',H2)
p('來源包含三篇數位時代文章、科技宅啊高、班老大、兩串 PTT 討論與天下雜誌文章。有日期的項目介於 2023-06-06 至 2023-08-04，一個來源未填日期。這些是文章日期，並非擷取時間。分析單位是選入的文字片段，同一篇文章可以有多段，不能視為獨立消費者。')
p('資料處理流程',H2)
table([['步驟','歷史材料與本次處理'],['蒐集與整理','Excel／Google Sheets 保存來源、標題、網址、日期及評論。PTT 表有原始行與清理後文字，原始爬蟲程式未恢復。'],['清理與翻譯','原始 81 段中有兩段合併為一段，另八段未保留文字。分析表有中文與英文欄位，但翻譯工具與逐筆刪除理由未保存。'],['情緒分析','原報告記載 Azure Machine Learning Excel 功能；保存 positive／neutral／negative 與分數。模型版本、請求及閾值未恢復。'],['文字探勘與視覺化','保存 CKIP 相容的詞性標註及 Power BI 詞雲；本次彙整 1,001 個帶詞性的詞項出現次數。'],['品質與可重現性','本次核對空白文字、排除 K82 平均值儲存格，以原始蒐集文字修復來源，並公開數值及詞頻衍生資料。']], [95,388])
p('新增的爬蟲與文字探勘範例',H2)
p('2026 年以 AI 協作新增 Python 程式：擷取 PTT 的 push-content 節點或新聞 article 內的段落，處理 HTML entities、空白與內容去重，排除評論者欄位與 IP。離線測試使用合成 HTML；選用即時擷取要求單一 HTTPS 網址、明列網域與 robots.txt 檢查。')
p('文字探勘範例明列 POS、停用詞與大小寫規則；TF-IDF 以合成、已斷詞文件示範。公開歷史詞頻沒有逐文件邊界，因此不宣稱重算了歷史 TF-IDF，也不宣稱原報告曾採用 TF-IDF。',SMALL)
story.append(PageBreak())

heading('03 / RESULTS AND QUALITY','A Different Denominator')
p('資料品質改變了正面比例',H2)
p('80 筆既有標籤為 42 正面、9 中立、29 負面，平均分數 0.500342，與原報告的四捨五入結果一致。然而，分析表 8 列已沒有評論文字，仍皆標成 positive，分數皆為 0.6611。空白成因未確認；現存空白不證明當時模型輸入也是空白。')
story.append(Bars())
table([['口徑','正面／中立／負面','平均既有分數'],['全部標籤，n=80','52.50% / 11.25% / 36.25%','0.500342'],['保留文字，n=72','47.22% / 12.50% / 40.28%','0.482481']], [150,210,123])
p('72 筆子集中，正面仍是最多的單一標籤，但未過半。這只改變資料分母，沒有修正模型語意誤判，也不能轉成市場購買意願。',BODY)
p('否定句與來源混合的影響',H2)
p('診斷案例包括：「沒有感覺到不適」被標為 negative／0.101464；「沒有出現眩暈情況」為 negative／0.186296；「不太明瞭的市場定位」卻為 positive／0.673467。這些是挑選來說明問題的案例，不是完整標註集，不能用來計算準確率。')
p('保留文字的紀錄中，40 筆來自論壇，32 筆是媒體或部落格節錄。不同來源與語域混合、片段來自同一文章、翻譯及否定語境，都限制了整體比例的解讀。')
p('詞頻與議題線索',H2)
p('依本次明列規則篩選歷史詞性詞表，「遊戲」出現 6 次、「內容」4 次、「軟體」4 次、「價格」3 次。它們只能描述保存的詞表，不能代表全部文字的完整詞頻。原詞雲中的 MR／AR 與金額字詞，適合用來提出技術期待與價格門檻等候選議題，仍需回看原句。',SMALL)
story.append(PageBreak())

heading('04 / CONCLUSION','Turning Signals into Questions')
p('對產業與消費者的用途',H2)
p('本研究的價值，是把規格討論拆解成可進一步研究的產品問題：技術是否吸引人、用途是否清楚、價格是否可接受，以及內容是否足以支持持續使用。對消費者，這也有助於區分技術讚賞與符合自身需求。')
table([['議題','研究方向','下一步驗證'],['產品定位','分開理解商務工作、開發者與一般消費用途','以分眾訪談及訊息理解測試確認'],['價格／版本','將價格疑慮與輕量版本期待視為假設','進行願付價格及方案測試，不能直接用少數留言訂價'],['內容生態系','追查遊戲、軟體與沉浸內容的具體需求','追蹤實際體驗、應用使用與留存']], [85,205,193])
p('原報告提出 AR／MR 發展、可接受的價格與輕量版本等建議。這些是探索性產品研究假設；沒有實施、營收改善或銷售因果驗證，不應改寫成已證實的產業成效。本文描述 2023 年討論，不作為目前的產品購買建議。')
p('如何讓下一輪研究更可靠',H2)
p('保留擷取與清理紀錄，以兩位標註者檢查中文整體情緒及價格、舒適度、顯示品質、用途等面向。比較翻譯前後輸出，依文章或討論串分組保留測試資料，報告逐類 precision、recall、F1 與否定句／諷刺錯誤。這些驗證尚未完成。')
p('來源與公開證據',H2)
p('原始證據：2023 年個人研究報告及其連結之蒐集、清理、翻譯、情緒與詞性中間資料。2026-10-28 讀取快照後新增數值重算、程式、圖表及本文。原報告與講義留在本機封存；公開專案不含完整評論集合、帳號、IP、學號及雲端分享連結。',SMALL)
p('GitHub：github.com/1121eason/NCKUxApple-VisionPro-SentimentAnalysis<br/>資料：data/historical_scores.csv、data/sources.csv、data/historical_token_counts.csv<br/>方法與結果：docs/methodology.md、docs/findings.md<br/>技術參考：Python HTMLParser／urllib.robotparser 官方文件；Google Sheets IMPORTXML 官方說明。',SMALL)
p('本機離線測試可驗證擷取規則及歷史數字對帳；本次未重新爬取歷史網站、呼叫 Azure、恢復 Power BI 專案或提交 Moodle。',SMALL)

def decorate(canvas,doc):
    width,height=A4
    canvas.setStrokeColor(colors.HexColor('#d4e1e8'));canvas.line(56,58,width-56,58)
    canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#637c8e'))
    canvas.drawString(56,41,'VISION PRO / NCKU / RESEARCH CASE STUDY')
    canvas.drawRightString(width-56,41,f'{doc.page} / 4')
    canvas.setTitle('Vision Pro: Web Scraping, Text Mining and Sentiment Analysis')
    canvas.setAuthor('Eason / Li Yi-Cheng')

output=ROOT/'docs/vision-pro-case-study.pdf'
doc=SimpleDocTemplate(str(output),pagesize=A4,leftMargin=56,rightMargin=56,topMargin=50,bottomMargin=78)
doc.build(story,onFirstPage=decorate,onLaterPages=decorate)
print(output)
