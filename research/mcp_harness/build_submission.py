"""Build SSRN form fields and a Russian submission guide from the final paper."""
from pathlib import Path
import json
import re
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from build_documents import link

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "submission"
REPO = "https://github.com/dmkkazakov/group-data-copilot"
RESEARCH = REPO + "/tree/main/research/mcp_harness"
VERIFIED_COMMIT = "306b74294ac2162a75054a6b26bd200f833ee6c7"
SOURCES = [
    ("Требования к подаче", "https://www.elsevier.support/ssrn/answer/get-started"),
    ("Раскрытие использования ИИ", "https://www.elsevier.support/ssrn/answer/AI"),
    ("Поля и этапы формы", "https://supportcontent.elsevier.com/Support%20Hub/SSRN/SSRN_NewSubmissionForm.pdf"),
    ("Лицензии SSRN", "https://www.elsevier.support/ssrn/answer/cc-licensing"),
    ("Классификация JEL", "https://www.aeaweb.org/jel/guide/jel.php"),
]


def main():
    OUT.mkdir(exist_ok=True)
    en = (ROOT / "paper_en.md").read_text(encoding="utf-8")
    title = en.splitlines()[0][2:]
    abstract = en.split("## Abstract\n\n", 1)[1].split("\n\nKeywords:", 1)[0]
    keywords = en.split("Keywords: ", 1)[1].split("\n", 1)[0].split("; ")
    ai = en.split("## AI assistance disclosure\n\n", 1)[1].split("\n\n", 1)[0]
    ethics = ("This study analyzes publicly available corporate disclosures and reports. "
              "It involved no recruitment, interventions, interviews, experiments with human participants "
              "or animals, or collection of non-public personal data. Individuals are discussed only in "
              "their publicly disclosed corporate roles or ownership capacities. No ethics committee "
              "approval or formal exemption determination is claimed.")
    funding = "This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors."
    conflict = "The author declares no personal or financial relationships that could have influenced, or could reasonably be perceived to have influenced, this research."
    data = ("The curated evidence corpus, source locators, code, tests and calculation outputs are available at "
            + RESEARCH + ". The verified research-code baseline is commit " + VERIFIED_COMMIT + ". "
            "The public issuer reports remain at their original URLs and are not redistributed. "
            "The corpus contains 40 selected assertions and does not claim complete group coverage.")
    meta = {
        "title": title, "abstract": abstract, "author": {"given_name": "Dmitry", "family_name": "Kazakov", "email": "dmkkazakov@gmail.com", "manuscript_author_line": "Independent research", "affiliation_for_profile": None, "orcid": None},
        "paper_date": "2026-10-30", "paper_version": "1.2", "corpus_schema_version": "1.1.0",
        "language": "English", "content_format": "Paper", "content_type": "Preprint",
        "upload_file": "Corporate_Groups_SSRN_EN.pdf", "keywords": keywords,
        "jel_codes": ["G32", "G34", "C88"],
        "suggested_classification_search_terms": ["Corporate Governance", "Corporate Finance", "Information Systems"],
        "classification_note": "Choose relevant subject matter classifications offered by the current SSRN form; these are search terms, not asserted classification IDs.",
        "ai_disclosure": ai, "ethics_statement": ethics, "data_availability": data,
        "funding_statement": {"text_if_true": funding, "author_confirmed": False},
        "competing_interests": {"text_if_true": conflict, "author_confirmed": False},
        "license_selection": None, "ssrn_id": None, "doi": None,
        "author_actions_before_submission": ["Review the entire manuscript and sources", "Confirm current author profile and affiliation", "Confirm or replace funding and competing-interest statements", "Select license and attest to upload rights"],
        "policy_check_date": "2026-10-30", "sources": [{"title": a, "url": b} for a,b in SOURCES],
        "abstract_word_count": len(abstract.split()), "abstract_character_count": len(abstract),
    }
    (OUT / "fields.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    texts = {
        "01_TITLE.txt": title,
        "02_ABSTRACT.txt": abstract,
        "03_KEYWORDS.txt": "\n".join(keywords),
        "04_JEL_CODES.txt": "G32\nG34\nC88",
        "05_AI_DISCLOSURE.txt": ai,
        "06_ETHICS_STATEMENT.txt": ethics,
        "07_DATA_AVAILABILITY.txt": data,
        "08_FUNDING_IF_TRUE.txt": "CONDITIONAL DRAFT — use only if factually correct and confirmed by the author. Do not paste this instruction.\n\n" + funding,
        "09_COMPETING_INTERESTS_IF_TRUE.txt": "CONDITIONAL DRAFT — use only if factually correct and confirmed by the author. Do not paste this instruction.\n\n" + conflict,
    }
    for name, content in texts.items():
        (OUT / name).write_text(content+"\n", encoding="utf-8")
    (OUT / "CITATION.bib").write_text("@unpublished{kazakov2026corporategroups,\n  author = {Kazakov, Dmitry},\n  title = {"+title+"},\n  year = {2026},\n  month = {October},\n  note = {Working paper, version 1.2; not yet submitted to SSRN},\n  url = {"+RESEARCH+"}\n}\n", encoding="utf-8")

    d=Document();sec=d.sections[0]
    sec.page_width=Inches(8.27);sec.page_height=Inches(11.69)
    sec.top_margin=sec.bottom_margin=Inches(.7)
    sec.left_margin=sec.right_margin=Inches(.76)
    normal=d.styles['Normal'];normal.font.name='Liberation Sans';normal.font.size=Pt(10.5)
    normal.paragraph_format.space_after=Pt(6);normal.paragraph_format.line_spacing=1.08
    for name,size in [('Title',22),('Heading 1',16),('Heading 2',12)]:
        st=d.styles[name];st.font.name='Liberation Sans';st.font.size=Pt(size);st.font.color.rgb=RGBColor(0,0,0)
        st.paragraph_format.space_before=Pt(10);st.paragraph_format.space_after=Pt(6);st.paragraph_format.keep_with_next=True
    def p(t,style=None):return d.add_paragraph(t,style)
    def heading(t):p(t,'Heading 1')
    def sub(t):p(t,'Heading 2')
    def url(label,target):
        x=p('');link(x,label,target)
    def table(rows):
        t=d.add_table(rows=0,cols=2);t.autofit=False
        t.columns[0].width=Inches(1.7);t.columns[1].width=Inches(4.95)
        borders=OxmlElement('w:tblBorders')
        for side in ['top','left','bottom','right','insideH','insideV']:
            el=OxmlElement('w:'+side);el.set(qn('w:val'),'single');el.set(qn('w:sz'),'4');el.set(qn('w:color'),'D9D9D9');borders.append(el)
        t._tbl.tblPr.append(borders)
        for i,(a,b) in enumerate(rows):
            row=t.add_row();row._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
            for j,text in enumerate((a,b)):
                cell=row.cells[j];cell.width=Inches(1.7 if j==0 else 4.95)
                par=cell.paragraphs[0];par.paragraph_format.space_before=Pt(5);par.paragraph_format.space_after=Pt(5)
                run=par.add_run(text);run.font.size=Pt(10);run.bold=(j==0)
                if i%2==0:
                    shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'EEF2F5');cell._tc.get_or_add_tcPr().append(shade)
        p('')

    p('Пакет публикации на SSRN','Title')
    p('Дмитрий Казаков · 30 октября 2026 года · версия статьи 1.2')
    p('Загрузите английский PDF. В нем уже находятся пять кейсов, 16 формул, источники и раскрытие использования ИИ. Эта инструкция и русская версия предназначены для автора.')
    heading('Что загрузить и что указать')
    table([('Файл','Corporate_Groups_SSRN_EN.pdf'),('Content Format','Paper'),('Content Type','Preprint'),('Language','English'),('Date paper was written','2026-10-30'),('Author','Dmitry Kazakov'),('Contact Author','Dmitry Kazakov'),('Email','dmkkazakov@gmail.com'),('Аффилиация','В рукописи: Independent research. В профиле укажите актуальные достоверные сведения; при изменении строки автора обновите PDF.'),('ORCID','Добавьте существующий ORCID, если он есть. Номер не создан и не подставлен.'),('DOI и SSRN ID','Пока отсутствуют; не заполняйте вымышленными значениями.')])
    sub('Классификация')
    p('Поиск в форме: Corporate Governance, Corporate Finance, Information Systems. Это рекомендации по тематике. Выберите подходящие подразделы из текущего списка формы. Коды JEL: G32, G34, C88.')
    url('Материалы и код на GitHub',RESEARCH)
    url('Проверки исследовательского кода на GitHub Actions',REPO+'/actions/runs/41121713624')

    d.add_page_break();heading('Текст для полей формы')
    sub('Title');p(title)
    sub('Abstract');p(abstract)
    p(f'Аннотация: {len(abstract.split())} слов, {len(abstract)} символов. Текст совпадает с английской рукописью.')
    sub('Keywords')
    p('Добавляйте каждое выражение отдельно и нажимайте Enter. Список для копирования — в 03_KEYWORDS.txt.')
    for kw in keywords:p(kw)
    sub('JEL Codes');p('G32 · G34 · C88. Вводите каждый код отдельно. Эти коды необязательны.')

    d.add_page_break();heading('Research Integrity')
    p('Английские тексты ниже подготовлены для соответствующих полей формы. Два заявления, зависящие от личных обстоятельств автора, выделены отдельно.')
    sub('Ethics statement');p(ethics)
    sub('AI disclosure');p(ai)
    sub('Data and software availability');p(data)
    sub('Funder statement при отсутствии грантов')
    p('Используйте следующий текст только если он верен. При наличии гранта, оплаты работы или иной поддержки раскройте источник и характер поддержки.')
    p(funding)
    sub('Declaration of Interest при отсутствии конфликта')
    p('Используйте следующий текст только если он верен. Занятость, консультации, владение активами и другие связи раскрываются, если они относятся к работе или могут восприниматься как влияющие на нее.')
    p(conflict)
    p('Авторское подтверждение содержательной проверки работы не проставлено автоматически. Перед Submit необходимо прочитать рукопись и подтвердить собственную ответственность за ее содержание.')

    d.add_page_break();heading('Порядок подачи')
    for text in [
        '1. Войдите в SSRN и начните новую подачу. Загрузите Corporate_Groups_SSRN_EN.pdf; формат Paper, тип Preprint.',
        '2. Проверьте извлеченные название и аннотацию. При ошибках вставьте тексты из файлов 01 и 02. Укажите дату, ключевые слова и автора.',
        '3. Выберите тематические подразделы и при необходимости добавьте JEL. Внесите применимые заявления Research Integrity.',
        '4. Проверьте авторские сведения, права на загрузку, личные декларации и выбранную лицензию. Затем нажмите Submit.',
        '5. После размещения сохраните постоянную ссылку и DOI, если он присвоен. Добавьте их в GitHub и библиографическую запись. До этого пакет не утверждает наличие публикации на SSRN.'
    ]:p(text)
    sub('Лицензия')
    p('Creative Commons на SSRN необязательна. Пока отдельное решение не принято, можно оставить стандартные условия SSRN без выбора CC. CC BY допускает переработку и коммерческое использование с указанием авторства; CC BY-NC-ND — распространение неизмененной работы с указанием авторства для некоммерческого использования. Выбор в форме не меняет лицензию кода и не отменяет ранее предоставленные разрешения.')
    sub('Что проверено')
    p('65 тестов: 48 исследовательских и 17 для CSV-приложения. Проверка GitHub Actions для версии исследовательского кода завершилась успешно. В эксперименте обнаружены все 520 внесенных искажений. Это не оценка точности автоматического извлечения фактов. Версия 1.2 уточняет раскрытие ИИ и добавляет пакет подачи; числа и корпус версии 1.1 не изменены.')
    p('В статье сохранены расхождение Berkshire на 0,051768 процентного пункта и ограничение повторного доступа к страницам МТС. Подготовка пакета не заменяет редакционную проверку SSRN.')
    sub('Официальные инструкции')
    for title_,u in SOURCES:url(title_,u)
    p('Требования проверены 30 октября 2026 года. Внешний вид формы может обновляться; сверяйте названия полей с текущим интерфейсом.')
    d.core_properties.title='Пакет публикации на SSRN'
    d.core_properties.author='Dmitry Kazakov'
    d.core_properties.subject=title
    for tree in (d.element, d.styles.element):
        for element in list(tree.iter(qn('w:pBdr'))):
            element.getparent().remove(element)
    d.save(OUT/'SSRN_GUIDE_RU.docx')
    print(json.dumps({'paper_version':'1.2','abstract_words':len(abstract.split()),'abstract_chars':len(abstract),'guide':str(OUT/'SSRN_GUIDE_RU.docx')},ensure_ascii=False))


if __name__ == '__main__':
    main()
