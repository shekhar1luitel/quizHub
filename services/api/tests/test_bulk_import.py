from io import BytesIO
from zipfile import ZipFile
from xml.sax.saxutils import escape
from sqlalchemy import select

from app.models.subject import Subject
from app.models.question import Option, Question, QuizQuestion
from app.models.quiz import Quiz
from app.services.bulk_import_service import parse_workbook

try:  # pragma: no cover - allow direct execution
    from .test_admin_management import _auth_headers
except ImportError:  # pragma: no cover
    from tests.test_admin_management import _auth_headers
from .test_auth import TestingSessionLocal, client


def _build_workbook() -> bytes:
    buffer = BytesIO()

    def build_sheet(rows: list[list[str | bool]]) -> str:
        def column_letter(index: int) -> str:
            letters = ""
            while index > 0:
                index, remainder = divmod(index - 1, 26)
                letters = chr(65 + remainder) + letters
            return letters

        xml_parts: list[str] = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">',
            "<sheetData>",
        ]
        for row_index, row_values in enumerate(rows, start=1):
            xml_parts.append(f'<row r="{row_index}">')
            for column_index, value in enumerate(row_values, start=1):
                if value is None:
                    continue
                cell_ref = f"{column_letter(column_index)}{row_index}"
                if isinstance(value, bool):
                    xml_parts.append(f'<c r="{cell_ref}" t="b"><v>{1 if value else 0}</v></c>')
                else:
                    xml_parts.append(
                        f'<c r="{cell_ref}" t="inlineStr"><is><t>{escape(str(value))}</t></is></c>'
                    )
            xml_parts.append("</row>")
        xml_parts.append("</sheetData></worksheet>")
        return "".join(xml_parts)

    subjects_rows = [
        ["Name", "Description", "Icon"],
        ["General Knowledge", "Mixed questions", "book"],
    ]
    quizzes_rows = [
        ["Title", "Description", "Is Active", "Questions"],
        ["General Quiz", "Quick starter quiz", True, "What is 2 + 2?"],
    ]
    questions_rows = [
        [
            "Prompt",
            "Explanation",
            "Subject",
            "Difficulty",
            "Is Active",
            "Subject",
            "Option 1",
            "Option 2",
            "Option 3",
            "Correct Option",
            "Quizzes",
        ],
        [
            "What is 2 + 2?",
            "Basic math.",
            "Mathematics",
            "Easy",
            True,
            "General Knowledge",
            "4",
            "5",
            "3",
            "Option 1",
            "General Quiz",
        ],
    ]

    with ZipFile(buffer, "w") as archive:
        archive.writestr(
            "[Content_Types].xml",
            """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/worksheets/sheet3.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
</Types>""",
        )
        archive.writestr(
            "_rels/.rels",
            """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>""",
        )
        archive.writestr(
            "xl/workbook.xml",
            """<?xml version="1.0" encoding="UTF-8"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets>
    <sheet name="Subjects" sheetId="1" r:id="rId1"/>
    <sheet name="Quizzes" sheetId="2" r:id="rId2"/>
    <sheet name="Questions" sheetId="3" r:id="rId3"/>
  </sheets>
</workbook>""",
        )
        archive.writestr(
            "xl/_rels/workbook.xml.rels",
            """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet2.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet3.xml"/>
</Relationships>""",
        )
        archive.writestr("xl/worksheets/sheet1.xml", build_sheet(subjects_rows))
        archive.writestr("xl/worksheets/sheet2.xml", build_sheet(quizzes_rows))
        archive.writestr("xl/worksheets/sheet3.xml", build_sheet(questions_rows))

    buffer.seek(0)
    return buffer.getvalue()


def test_bulk_import_template_download():
    headers = _auth_headers()
    response = client.get(
        "/api/admin/bulk-import/template",
        headers=headers,
    )
    assert response.status_code == 200
    workbook = parse_workbook(response.content)
    assert workbook.subjects
    assert workbook.questions


def test_bulk_import_preview_and_commit():
    headers = _auth_headers()
    content = _build_workbook()

    preview_response = client.post(
        "/api/admin/bulk-import/preview",
        files={
            "file": (
                "bulk.xlsx",
                content,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
        headers=headers,
    )
    assert preview_response.status_code == 200
    preview = preview_response.json()
    assert preview["subjects"][0]["action"] == "create"
    assert preview["quizzes"][0]["action"] == "create"
    assert preview["questions"][0]["action"] == "create"

    commit_payload = {
        "subjects": [
            {"name": "General Knowledge", "description": "Mixed questions", "icon": "book"}
        ],
        "questions": [
            {
                "prompt": "What is 2 + 2?",
                "explanation": "Basic math.",
                "subject": "Mathematics",
                "difficulty": "Easy",
                "is_active": True,
                "subject_name": "General Knowledge",
                "quiz_titles": ["General Quiz"],
                "options": [
                    {"text": "4", "is_correct": True},
                    {"text": "5", "is_correct": False},
                    {"text": "3", "is_correct": False},
                ],
            }
        ],
        "quizzes": [
            {
                "title": "General Quiz",
                "description": "Quick starter quiz",
                "is_active": True,
                "question_prompts": ["What is 2 + 2?"],
            }
        ],
    }

    commit_response = client.post(
        "/api/admin/bulk-import/commit",
        json=commit_payload,
        headers=headers,
    )
    assert commit_response.status_code == 200
    result = commit_response.json()
    assert result["subjects_created"] == 1
    assert result["questions_created"] == 1
    assert result["quizzes_created"] == 1

    session = TestingSessionLocal()
    try:
        subject = session.execute(
            select(Subject).where(Subject.slug == "general-knowledge")
        ).scalar_one()
        question = session.execute(
            select(Question).where(Question.prompt == "What is 2 + 2?")
        ).scalar_one()
        quiz = session.execute(select(Quiz).where(Quiz.title == "General Quiz")).scalar_one()
        options = session.execute(
            select(Option).where(Option.question_id == question.id)
        ).scalars().all()
        quiz_questions = session.execute(
            select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id)
        ).scalars().all()
    finally:
        session.close()

    export_response = client.get(
        "/api/admin/bulk-import/export",
        headers=headers,
    )
    assert export_response.status_code == 200
    exported = parse_workbook(export_response.content)
    assert any(subject.name == "General Knowledge" for subject in exported.subjects)
    assert any(question.prompt == "What is 2 + 2?" for question in exported.questions)

    assert subject.description == "Mixed questions"
    assert question.explanation == "Basic math."
    assert len(options) == 3
    assert any(option.is_correct for option in options)
    assert len(quiz_questions) == 1

    # preview again should mark everything as update
    repeat_preview = client.post(
        "/api/admin/bulk-import/preview",
        files={
            "file": (
                "bulk.xlsx",
                content,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
        headers=headers,
    )
    assert repeat_preview.status_code == 200
    repeat_data = repeat_preview.json()
    assert repeat_data["subjects"][0]["action"] == "update"
    assert repeat_data["quizzes"][0]["action"] == "update"
    assert repeat_data["questions"][0]["action"] == "update"
