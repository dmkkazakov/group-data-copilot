"""Build both manuscripts from Markdown; document dependencies are optional."""
from pathlib import Path
import re
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from matplotlib.mathtext import math_to_image
from matplotlib.font_manager import FontProperties
from PIL import Image

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"artifacts";FIG=ROOT/"figures"

def link(p,label,url):
    h=OxmlElement("w:hyperlink");h.set(qn("r:id"),p.part.relate_to(url,RT.HYPERLINK,is_external=True))
    r=OxmlElement("w:r");pr=OxmlElement("w:rPr");color=OxmlElement("w:color");color.set(qn("w:val"),"000000");pr.append(color)
    u=OxmlElement("w:u");u.set(qn("w:val"),"single");pr.append(u);r.append(pr)
    t=OxmlElement("w:t");t.text=label;r.append(t);h.append(r);p._p.append(h)

def paragraph(doc,text,style=None):
    p=doc.add_paragraph(style=style)
    for chunk in re.split(r"(https?://\S+)",text):
        if chunk.startswith("http"):
            url=chunk.rstrip(".")
            link(p,"[online source]" if style=="Reference" else url,url)
            if chunk.endswith("."):p.add_run(".")
        else:
            for bit in re.split(r"(\b(?:t_v|t_k|W_ij|n_ik|N_k|a_k|v_k)\b)",chunk):
                if re.fullmatch(r"(?:t_v|t_k|W_ij|n_ik|N_k|a_k|v_k)",bit):
                    a,b=bit.split("_");p.add_run(a);r=p.add_run(b);r.font.subscript=True
                else:p.add_run(bit)
    return p

def table(doc,lines):
    rows=[[x.strip() for x in line.strip().strip("|").split("|")] for line in lines]
    rows=[r for r in rows if not all(re.fullmatch(r"[:\- ]+",c) for c in r)]
    n=len(rows[0]);t=doc.add_table(rows=0, cols=n);t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
    widths=([3.1,1.55,2.15] if n==3 else [6.8/n]*n)
    if rows[0][0] in ["Case","Кейс"]:widths=[1.0,2.8,3.0]
    for i,w in enumerate(widths):t.columns[i].width=Inches(w)
    pr=t._tbl.tblPr
    borders=OxmlElement("w:tblBorders")
    for k in ["top","left","bottom","right","insideH","insideV"]:
        b=OxmlElement("w:"+k);b.set(qn("w:val"),"single");b.set(qn("w:sz"),"4");b.set(qn("w:color"),"D9D9D9");borders.append(b)
    pr.append(borders)
    for ri,data in enumerate(rows):
        row=t.add_row();trpr=row._tr.get_or_add_trPr();trpr.append(OxmlElement("w:cantSplit"))
        if ri==0:trpr.append(OxmlElement("w:tblHeader"))
        for ci,txt in enumerate(data):
            c=row.cells[ci];c.width=Inches(widths[ci]);c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            tcpr=c._tc.get_or_add_tcPr();mar=OxmlElement("w:tcMar")
            for edge in ["top","bottom","left","right"]:
                v=OxmlElement("w:"+edge);v.set(qn("w:w"),"85");v.set(qn("w:type"),"dxa");mar.append(v)
            tcpr.append(mar)
            if ri==0 or ri%2==0:
                shade=OxmlElement("w:shd");shade.set(qn("w:fill"),"E6EBEF" if ri==0 else "F7F8F9");tcpr.append(shade)
            p=c.paragraphs[0];p.paragraph_format.space_after=Pt(2);p.paragraph_format.space_before=Pt(2);p.paragraph_format.line_spacing=1.03
            if ci>0 and len(txt)<35:p.alignment=WD_ALIGN_PARAGRAPH.CENTER
            r=p.add_run(txt);r.font.name="Liberation Serif";r.font.size=Pt(9.5);r.bold=(ri==0)
    doc.add_paragraph().paragraph_format.space_after=Pt(1)

def build(lang):
    source=(ROOT/f"paper_{lang}.md").read_text(encoding="utf-8")
    if lang=="ru":
        refs=(ROOT/"paper_en.md").read_text(encoding="utf-8").split("## References\n",1)[1]
        source=source.split("## Источники\n",1)[0] + "## Источники\n\n" + refs
    d=Document();s=d.sections[0];s.page_width=Inches(8.5);s.page_height=Inches(11)
    s.top_margin=Inches(.72);s.bottom_margin=Inches(.7);s.left_margin=Inches(.75);s.right_margin=Inches(.75)
    s.header_distance=Inches(.28);s.footer_distance=Inches(.3)
    normal=d.styles["Normal"];normal.font.name="Liberation Serif";normal.font.size=Pt(10.5)
    normal.paragraph_format.line_spacing=1.05;normal.paragraph_format.space_after=Pt(5)
    for name,size in [("Title",21),("Heading 1",14),("Heading 2",12)]:
        st=d.styles[name];st.font.name="Liberation Sans";st.font.size=Pt(size);st.font.color.rgb=RGBColor(0,0,0)
        st.paragraph_format.space_before=Pt(14 if name!="Title" else 0);st.paragraph_format.space_after=Pt(7)
        st.paragraph_format.keep_with_next=True
    ref=d.styles.add_style("Reference",1);ref.base_style=normal;ref.font.size=Pt(9.5);ref.paragraph_format.space_after=Pt(7)
    footer=s.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
    rr=footer.add_run("Kazakov · MCP and corporate groups  |  ");rr.font.size=Pt(8)
    field=OxmlElement("w:fldSimple");field.set(qn("w:instr"),"PAGE");footer._p.append(field)
    lines=source.splitlines();i=0;refs=False
    while i<len(lines):
        line=lines[i].strip()
        if not line:i+=1;continue
        if line=="<!-- pagebreak -->":d.add_page_break();i+=1;continue
        if line.startswith("# "):paragraph(d,line[2:],"Title")
        elif line.startswith("## "):
            text=line[3:];refs=text in ["References","Источники"]
            paragraph(d,text,"Heading 1")
        elif line.startswith("### "):paragraph(d,line[4:],"Heading 2")
        elif line.startswith("|"):
            group=[]
            while i<len(lines) and lines[i].strip().startswith("|"):group.append(lines[i]);i+=1
            table(d,group);continue
        elif line.startswith("$$"):
            expr=line[2:-2].strip();num=re.search(r"\\tag\{(\d+)\}",expr).group(1)
            expr=re.sub(r"\s*\\tag\{\d+\}","",expr)
            img=FIG/f"equation_{num}.png"
            math_to_image("$"+expr+"$",str(img),prop=FontProperties(size=12),dpi=300,color="black")
            w,h=Image.open(img).size
            p=d.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.space_before=Pt(6);p.paragraph_format.space_after=Pt(9)
            p.add_run().add_picture(str(img),width=Inches(min(w/300,5.95)))
            p.add_run("   ("+num+")").font.size=Pt(10)
        elif line.startswith("<!--"):pass
        else:paragraph(d,line,"Reference" if refs else None)
        i+=1
    # Remove inherited title borders and keep all headings black.
    for elem in list(d.element.iter(qn("w:pBdr"))):elem.getparent().remove(elem)
    for elem in list(d.styles.element.iter(qn("w:pBdr"))):elem.getparent().remove(elem)
    d.core_properties.author="Dmitry Kazakov";d.core_properties.title=lines[0][2:]
    d.core_properties.subject="Five public corporate-group cases and reproducible MCP harness"
    name="Corporate_Groups_SSRN_EN.docx" if lang=="en" else "MCP_Harness_Corporate_Groups.docx"
    d.save(OUT/name);print(OUT/name)

if __name__=="__main__":
    OUT.mkdir(exist_ok=True);FIG.mkdir(exist_ok=True)
    build("en");build("ru")
