# surveys.export

# PYTHON
import StringIO    
import csv

# DJANGO
from django.utils.encoding import smart_str

# PYRTF
import PyRTF

# RTFUNICODE
import rtfunicode

# SURVEYS
from .models import Answer 

#############
# SPREADSHEET
#############
def survey_to_text(questions, respondents):
    lines = []
    for respondent in respondents:
        answers = Answer.objects.filter(
                            respondent=respondent,
                            question__in=questions).order_by('question__number')
        if answers:
            survey_date = answers[0].created.isoformat()
            lines.append(smart_str(u'Respondent (%d): %s' % 
                        (respondent.id, respondent.pref_name())))
            lines.append(smart_str(u'Date: %s' % survey_date))
            lines.append('')
            for answer in answers:
                lines.append(smart_str(unicode(answer.question)))
                lines.append(smart_str(answer.text))
                lines.append('')
    return u'\n'.join(lines)
    
def survey_to_excel(questions, respondents):
    rowheadings = ["RESPONDENT ID", "RESPONDENT NAME", "DATE"]
    rowheadings.extend([question.text for question in questions])
    excelfile = StringIO.StringIO()
    writer = csv.writer(excelfile, dialect='excel')
    writer.writerow(rowheadings)
    for respondent in respondents:
        answers = Answer.objects.filter(
                            respondent=respondent,
                            question__in=questions).order_by('question__number')
        if answers:
            survey_date = smart_str(answers[0].created.isoformat())
            answers = {a.question:a for a in answers}
            row = [respondent.id, smart_str(respondent.pref_name()), survey_date]
            for q in questions:
                answer = answers.get(q, None)
                if answer:
                    row.append(smart_str(answer.text))
                else:
                    row.append('')
            writer.writerow(row)
    exceldata = excelfile.getvalue()
    excelfile.close()
    return exceldata
    
#####
# RTF
#####
def survey_to_rtf(questions, respondents):
    doc = PyRTF.Document()
    ss = doc.StyleSheet
    first_page = True
    for respondent in respondents:
        answers = Answer.objects.filter(
                            respondent=respondent,
                            question__in=questions).order_by('question__number')
        if answers:
            section = PyRTF.Section()
            if first_page:
                first_page = False
                p = PyRTF.Paragraph(ss.ParagraphStyles.Heading1)
            else:
                p = PyRTF.Paragraph(ss.ParagraphStyles.Heading1, 
                            PyRTF.ParagraphPS().SetPageBreakBefore(True))
            title_name = u'Respondent %d: %s' % (respondent.id, respondent.pref_name())
            title_date = u'Date: %s' % answers[0].created.strftime('%d %B %Y %I:%M:%S %p')
            p.append(title_name.encode('rtfunicode'))
            section.append(p)
            p = PyRTF.Paragraph(ss.ParagraphStyles.Heading2)
            p.append(title_date.encode('rtfunicode'))
            section.append(p)
            section.append('')
            for answer in answers:
                p = PyRTF.Paragraph(ss.ParagraphStyles.Normal)
                p.append(PyRTF.B(unicode(answer.question).encode('rtfunicode')))
                section.append(p)
                p = PyRTF.Paragraph(ss.ParagraphStyles.Normal)
                p.append(unicode(answer.text).encode('rtfunicode'))
                section.append(p)
                section.append('')
            doc.Sections.append(section)
    rtffile = StringIO.StringIO()
    writer = PyRTF.Renderer()
    writer.Write(doc, rtffile)
    rtfdata = rtffile.getvalue()
    rtffile.close()
    return rtfdata
