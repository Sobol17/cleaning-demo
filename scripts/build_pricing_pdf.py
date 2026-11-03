from pathlib import Path
import re, html
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/pdf/yasno-packages-2026-10-31.pdf'
FONT='/System/Library/Fonts/Supplemental/'
for name,file in [('Arial','Arial.ttf'),('Arial-Bold','Arial Bold.ttf'),('Arial-Italic','Arial Italic.ttf')]:
    pdfmetrics.registerFont(TTFont(name,FONT+file))
pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='Arial-Bold',italic='Arial-Italic',boldItalic='Arial-Bold')
C=colors.HexColor
styles={
'p':ParagraphStyle('body',fontName='Arial',fontSize=9.3,leading=13.3,spaceAfter=8,textColor=C('#203047')),
'h1':ParagraphStyle('h1',fontName='Arial-Bold',fontSize=21,leading=25,spaceAfter=17,textColor=C('#133D77')),
'h2':ParagraphStyle('h2',fontName='Arial-Bold',fontSize=18,leading=23,spaceAfter=13,textColor=C('#133D77')),
'h3':ParagraphStyle('h3',fontName='Arial-Bold',fontSize=11.8,leading=16,spaceBefore=9,spaceAfter=7,textColor=C('#133D77')),
'cell':ParagraphStyle('cell',fontName='Arial',fontSize=8.2,leading=11,spaceAfter=0,textColor=C('#203047')),
'head':ParagraphStyle('head',fontName='Arial-Bold',fontSize=8.2,leading=11,spaceAfter=0,textColor=colors.white),
'url':ParagraphStyle('url',fontName='Arial',fontSize=7.2,leading=9,spaceAfter=7,textColor=C('#2265AE'),splitLongWords=True),
}
W=499.27

def fmt(t):
    t=html.escape(t.replace('₽', 'руб.'))
    t=re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',t)
    return t.replace('—','-').replace('–','-').replace('\u2011','-')

def table(lines):
    rows=[[c.strip() for c in l.strip().strip('|').split('|')] for l in lines]
    rows=[r for r in rows if not all(re.fullmatch(r'[:\- ]+',c) for c in r)]
    n=len(rows[0])
    ratios={3:[.28,.55,.17],4:[.40,.20,.20,.20],5:[.31,.10,.20,.19,.20]}[n]
    if n==3 and 'Раньше' in rows[0][0]: ratios=[.34,.36,.30]
    if n==3 and 'Источник' in rows[0][0]: ratios=[.26,.39,.35]
    data=[[Paragraph(fmt(c),styles['head' if i==0 else 'cell']) for c in row] for i,row in enumerate(rows)]
    t=Table(data,colWidths=[W*x for x in ratios],repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),C('#174C8A')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('ROWBACKGROUNDS',(0,1),(-1,-1),[C('#F0F5FB'),colors.white]),('LINEBELOW',(0,0),(-1,0),.6,C('#174C8A')),('LINEBELOW',(0,1),(-1,-1),.3,C('#DDE6F0'))]))
    return t

def chrome(canvas,doc):
    canvas.saveState(); canvas.setStrokeColor(C('#DDE6F0')); canvas.setLineWidth(.5)
    canvas.line(48,799,547,799); canvas.line(48,40,547,40)
    canvas.setFillColor(C('#60748E')); canvas.setFont('Arial',8)
    canvas.drawString(48,811,'ЯСНО  /  САЙТ И CRM ДЛЯ КЛИНИНГА')
    canvas.drawRightString(547,811,'03.11.2026  ·  КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ')
    canvas.drawString(48,26,'Состав пакетов, стоимость и условия обслуживания')
    canvas.drawRightString(547,26,str(doc.page)); canvas.restoreState()

lines=(ROOT/'docs/pricing-2026-10-31.md').read_text().splitlines(); story=[]; i=0
while i<len(lines):
    l=lines[i].strip()
    if not l: i+=1; continue
    if l=='---': story.append(PageBreak()); i+=1; continue
    if l.startswith('|'):
        chunk=[]
        while i<len(lines) and lines[i].startswith('|'): chunk.append(lines[i]); i+=1
        story += [table(chunk),Spacer(1,10)]; continue
    if l.startswith('http'):
        story.append(Paragraph('<link href="'+html.escape(l,quote=True)+'">'+fmt(l)+'</link>',styles['url']))
    elif l.startswith('#'):
        level=len(l)-len(l.lstrip('#')); story.append(Paragraph(fmt(l[level:].strip()),styles['h'+str(min(level,3))]))
    else: story.append(Paragraph(fmt(l),styles['p']))
    i+=1
OUT.parent.mkdir(parents=True,exist_ok=True)
SimpleDocTemplate(str(OUT),pagesize=(595.27,841.89),leftMargin=48,rightMargin=48,topMargin=59,bottomMargin=54,title='Ясно: пакеты и прозрачная стоимость',author='Ясно',subject='Тарифы сайта и CRM для клининга. Иркутск. 03.11.2026').build(story,onFirstPage=chrome,onLaterPages=chrome)
print(OUT)
