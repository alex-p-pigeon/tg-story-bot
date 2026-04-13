from datetime import datetime, date, timezone, timedelta

print("import Start:", datetime.now().time().strftime("%H:%M:%S"))

import io
import tempfile

import shutil
import zipfile

from telethon import TelegramClient, events, errors
from telethon.tl.custom import Button
from telethon.tl.types import InputPeerUser
from telethon.errors import UserIsBlockedError
import asyncio
import sys, os

# PDF generation
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# custom functions
import fpgDB as pgDB
from config_reader import config

print("import End:", datetime.now().time().strftime("%H:%M:%S"))

api_id = config.TG_API_ID.get_secret_value()
api_hash = config.TG_API_HASH.get_secret_value()
bot_token = config.bot_token.get_secret_value()

bot_id = int(bot_token.split(":")[0])

bot = TelegramClient('metrics', api_id, api_hash, timeout=20).start(bot_token=bot_token)


# -----------------------------------------------------------------------------------------------------------------------------------------------
def get_next_run_time():
    """Calculate the next run time at 21:00 today or tomorrow if it's already past 21:00"""
    now = datetime.now()
    today_21 = now.replace(hour=21, minute=0, second=0, microsecond=0)

    if now < today_21:
        return today_21
    else:
        tomorrow_21 = today_21 + timedelta(days=1)
        return tomorrow_21


def create_daily_calendar_table(daily_data):
    """Create a weekly calendar table from daily data"""
    daily_dict = {row[0]: row[1] for row in daily_data} if daily_data else {}

    start_date = datetime.now().date() - timedelta(days=29)

    calendar_data = [['Week', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']]

    current_date = start_date
    week_num = 1
    week_row = [f'Week {week_num}']

    days_since_monday = current_date.weekday()
    week_start = current_date - timedelta(days=days_since_monday)

    for day_offset in range(7 * 5):
        cal_date = week_start + timedelta(days=day_offset)

        if day_offset > 0 and day_offset % 7 == 0:
            calendar_data.append(week_row)
            week_num += 1
            week_row = [f'Week {week_num}']

        if cal_date < start_date or cal_date > datetime.now().date():
            week_row.append('-')
        else:
            user_count = daily_dict.get(cal_date, 0)
            week_row.append(str(user_count))

    if len(week_row) > 1:
        while len(week_row) < 8:
            week_row.append('-')
        calendar_data.append(week_row)

    return calendar_data

def aggregate_weekly(daily_data):
    """Агрегирует daily_data по 4 неделям, начиная с 4 недель назад"""
    today = datetime.now().date()
    weeks = {}
    for row in daily_data:
        day, count = row[0], row[1]
        days_ago = (today - day).days      # сколько дней назад
        week_num = days_ago // 7           # 0=текущая, 1=прошлая, ...
        if week_num <= 3:
            label = f'week -{week_num + 1}'
            weeks[label] = weeks.get(label, 0) + count

    # Возвращаем в порядке week-4 .. week-1
    return {f'week -{i}': weeks.get(f'week -{i}', 0) for i in range(4, 0, -1)}

def create_pdf_report(user_status_data, daily_data, activity_data, detailed_activity_data, action_summary_data,
                      blocked_users_data, mau_data, start_only_count, filename, speakpal_count):
    """Create a PDF report with user metrics tables including blocked users and MAU funnel"""
    doc = SimpleDocTemplate(filename, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1,
    )

    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=15,
        spaceBefore=20,
        alignment=0,
    )

    title = Paragraph("User Activity Report", title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))

    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=1,
    )
    date_text = Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", date_style)
    elements.append(date_text)
    elements.append(Spacer(1, 20))

    # ------------------------------------------------------------------
    # SECTION 1: MAU Funnel (новый раздел)
    # ------------------------------------------------------------------
    section1_title = Paragraph("1. MAU Funnel (30 Days)", section_title_style)
    elements.append(section1_title)

    # Вычисляем значения воронки
    total_mau     = mau_data[0][2] if mau_data and len(mau_data) > 0 else 0
    engaged_users = user_status_data[0][2] if user_status_data and len(user_status_data) > 0 else 0
    start_only    = start_only_count if start_only_count is not None else 0
    conversion    = round(engaged_users / total_mau * 100, 1) if total_mau > 0 else 0

    funnel_table_data = [
        ['Метрика', 'Значение', 'Описание'],
        ['MAU total (≈ Telegram)', str(total_mau),    'Все пользователи, писавшие боту за 30д'],
        ['  — Start-only',         str(start_only),   'Нажали Start, но не сделали ни одного действия'],
        ['  — Engaged users',      str(engaged_users),'Совершили хотя бы одно действие внутри бота'],
        ['Конверсия Start→Action', f'{conversion}%',  'engaged / MAU total'],
        ['  — из них SpeakPal', str(speakpal_count), 'Пользователи SpeakPal за 30д (c_log4=1)'],
    ]

    funnel_table = Table(funnel_table_data, colWidths=[2.2 * inch, 1.2 * inch, 3.0 * inch])
    funnel_table.setStyle(TableStyle([
        ('BACKGROUND',  (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR',   (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN',       (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME',    (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',    (0, 0), (-1, 0), 10),
        ('FONTNAME',    (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE',    (0, 1), (-1, -1), 9),
        ('ALIGN',       (2, 1), (2, -1), 'LEFT'),
        ('GRID',        (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN',      (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.lightcyan, colors.lightblue]),
        # Выделяем строку конверсии
        ('BACKGROUND',  (0, 4), (-1, 4), colors.lightyellow),
        ('FONTNAME',    (0, 4), (-1, 4), 'Helvetica-Bold'),
    ]))
    elements.append(funnel_table)

    elements.append(Spacer(1, 15))
    funnel_summary_text = f"""
    <b>Funnel Summary (30 дней):</b><br/>
    • MAU total (≈ Telegram MAU): {total_mau}<br/>
    • Start-only пользователи: {start_only} — нажали Start, но дальше не пошли<br/>
    • Engaged users: {engaged_users} — реально пользуются ботом<br/>
    • Конверсия Start → Action: {conversion}%<br/>
    """
    elements.append(Paragraph(funnel_summary_text, styles['Normal']))

    # ------------------------------------------------------------------
    # SECTION 2: Active Users Overview (DAU / WAU / MAU из t_user_status)
    # ------------------------------------------------------------------
    elements.append(Spacer(1, 25))
    section2_title = Paragraph("2. Active Users Overview (DAU / WAU / MAU)", section_title_style)
    elements.append(section2_title)

    if user_status_data and len(user_status_data) > 0:
        status_row = user_status_data[0]

        status_table_data = [
            ['Period', 'Active Users (engaged)'],
            ['Last 24 Hours', str(status_row[0])],
            ['Last 7 Days',   str(status_row[1])],
            ['Last 30 Days',  str(status_row[2])],
        ]

        status_table = Table(status_table_data, colWidths=[3 * inch, 3 * inch])
        status_table.setStyle(TableStyle([
            ('BACKGROUND',  (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR',   (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN',       (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME',    (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE',    (0, 0), (-1, 0), 11),
            ('FONTNAME',    (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE',    (0, 1), (-1, -1), 10),
            ('GRID',        (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN',      (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.lightcyan, colors.lightblue]),
        ]))
        elements.append(status_table)

        elements.append(Spacer(1, 15))
        status_summary_text = f"""
        <b>Status Summary:</b><br/>
        • Daily Active Users: {status_row[0]}<br/>
        • Weekly Active Users: {status_row[1]}<br/>
        • Monthly Active Users: {status_row[2]}<br/>
        """
        elements.append(Paragraph(status_summary_text, styles['Normal']))
    else:
        elements.append(Paragraph("No user status data found.", styles['Normal']))

    # ------------------------------------------------------------------
    # SECTION 3: Blocked Users Report
    # ------------------------------------------------------------------
    elements.append(Spacer(1, 25))
    section3_title = Paragraph("3. Blocked Users Report", section_title_style)
    elements.append(section3_title)

    if blocked_users_data and len(blocked_users_data) > 0:
        blocked_table_data = [['Period', 'Blocked Users Count']]
        for row in blocked_users_data:
            blocked_table_data.append([str(row[0]), str(row[1])])

        blocked_table = Table(blocked_table_data, colWidths=[3 * inch, 3 * inch])
        blocked_table.setStyle(TableStyle([
            ('BACKGROUND',  (0, 0), (-1, 0), colors.darkred),
            ('TEXTCOLOR',   (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN',       (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME',    (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE',    (0, 0), (-1, 0), 11),
            ('FONTNAME',    (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE',    (0, 1), (-1, -1), 10),
            ('GRID',        (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN',      (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightcoral]),
        ]))
        elements.append(blocked_table)

        elements.append(Spacer(1, 15))
        blocked_today = blocked_users_data[0][1] if len(blocked_users_data) > 0 else 0
        blocked_week  = blocked_users_data[1][1] if len(blocked_users_data) > 1 else 0
        blocked_month = blocked_users_data[2][1] if len(blocked_users_data) > 2 else 0

        blocked_summary_text = f"""
        <b>Blocked Users Summary:</b><br/>
        • Users blocked today: {blocked_today}<br/>
        • Users blocked this week: {blocked_week}<br/>
        • Users blocked this month: {blocked_month}<br/>
        """
        elements.append(Paragraph(blocked_summary_text, styles['Normal']))
    else:
        elements.append(Paragraph("No blocked users data found.", styles['Normal']))

    # ------------------------------------------------------------------
    # SECTION 4: Daily Activity Calendar
    # ------------------------------------------------------------------
    elements.append(Spacer(1, 25))
    section4_title = Paragraph("4. Daily Activity Calendar (Last 30 Days)", section_title_style)
    elements.append(section4_title)

    if daily_data:
        calendar_table_data = create_daily_calendar_table(daily_data)

        calendar_table = Table(
            calendar_table_data,
            colWidths=[0.8 * inch] * 8
        )
        calendar_table.setStyle(TableStyle([
            ('BACKGROUND',  (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR',   (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN',       (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME',    (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE',    (0, 0), (-1, 0), 10),
            ('BACKGROUND',  (0, 1), (0, -1), colors.lightgreen),
            ('FONTNAME',    (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE',    (0, 1), (0, -1), 9),
            ('BACKGROUND',  (1, 1), (-1, -1), colors.white),
            ('FONTNAME',    (1, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE',    (1, 1), (-1, -1), 8),
            ('GRID',        (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN',      (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND',  (6, 0), (6, 0), colors.green),
            ('BACKGROUND',  (7, 0), (7, 0), colors.green),
            ('BACKGROUND',  (6, 1), (6, -1), colors.lightgrey),
            ('BACKGROUND',  (7, 1), (7, -1), colors.lightgrey),
        ]))
        elements.append(calendar_table)

        elements.append(Spacer(1, 15))
        total_daily_users = sum(row[1] for row in daily_data)
        avg_daily_users   = round(total_daily_users / len(daily_data), 1) if daily_data else 0
        max_daily_users   = max(row[1] for row in daily_data) if daily_data else 0
        min_daily_users   = min(row[1] for row in daily_data) if daily_data else 0

        calendar_summary_text = f"""
        <b>Calendar Summary:</b><br/>
        • Average daily active users: {avg_daily_users}<br/>
        • Peak daily active users: {max_daily_users}<br/>
        • Minimum daily active users: {min_daily_users}<br/>
        • Total user-days: {total_daily_users}<br/>
        """
        elements.append(Paragraph(calendar_summary_text, styles['Normal']))
    else:
        elements.append(Paragraph("No daily activity data found.", styles['Normal']))

    # ------------------------------------------------------------------
    # SECTION 5: User Actions Breakdown
    # ------------------------------------------------------------------
    elements.append(Spacer(1, 25))
    section5_title = Paragraph("5. User Actions Breakdown", section_title_style)
    elements.append(section5_title)

    if activity_data:
        table_data = [['User ID', 'Week Actions', 'Month Actions']]
        for row in activity_data:
            table_data.append([str(row[0]), str(row[1]), str(row[2])])

        activity_table = Table(table_data, colWidths=[2 * inch, 2 * inch, 2 * inch])
        activity_table.setStyle(TableStyle([
            ('BACKGROUND',  (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR',   (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN',       (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME',    (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE',    (0, 0), (-1, 0), 11),
            ('FONTNAME',    (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE',    (0, 1), (-1, -1), 9),
            ('GRID',        (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN',      (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        elements.append(activity_table)

        elements.append(Spacer(1, 15))
        total_users        = len(activity_data)
        total_week_actions = sum(row[1] for row in activity_data)
        total_month_actions= sum(row[2] for row in activity_data)

        activity_summary_text = f"""
        <b>Actions Summary:</b><br/>
        • Active Users with Actions: {total_users}<br/>
        • Total Week Actions: {total_week_actions}<br/>
        • Total Month Actions: {total_month_actions}<br/>
        """
        elements.append(Paragraph(activity_summary_text, styles['Normal']))
    else:
        elements.append(Paragraph("No user activity data found for the specified period.", styles['Normal']))

    # ------------------------------------------------------------------
    # SECTION 6: Detailed User Actions Report
    # ------------------------------------------------------------------
    elements.append(Spacer(1, 25))
    section6_title = Paragraph("6. Detailed User Actions Report", section_title_style)
    elements.append(section6_title)

    if detailed_activity_data:
        detailed_table_data = [['User ID', 'Action', 'Comment', 'Week Count', 'Month Count']]
        for row in detailed_activity_data:
            comment_raw = str(row[2]) if row[2] else ''
            comment_trunc = comment_raw[:30] + ('...' if len(comment_raw) > 30 else '')
            detailed_table_data.append([
                str(row[0]),
                str(row[1]) if row[1] else '',
                comment_trunc,
                str(row[3]),
                str(row[4]),
            ])

        detailed_activity_table = Table(
            detailed_table_data,
            colWidths=[1.2 * inch, 1.2 * inch, 2.2 * inch, 1 * inch, 1 * inch]
        )
        detailed_activity_table.setStyle(TableStyle([
            ('BACKGROUND',  (0, 0), (-1, 0), colors.purple),
            ('TEXTCOLOR',   (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN',       (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME',    (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE',    (0, 0), (-1, 0), 10),
            ('FONTNAME',    (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE',    (0, 1), (-1, -1), 8),
            ('GRID',        (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN',      (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        elements.append(detailed_activity_table)

        elements.append(Spacer(1, 15))
        total_detailed_records = len(detailed_activity_data)
        unique_users    = len(set(row[0] for row in detailed_activity_data))
        unique_actions  = len(set(row[1] for row in detailed_activity_data if row[1]))
        total_det_week  = sum(row[3] for row in detailed_activity_data)
        total_det_month = sum(row[4] for row in detailed_activity_data)

        detailed_summary_text = f"""
        <b>Detailed Actions Summary:</b><br/>
        • Total action records: {total_detailed_records}<br/>
        • Unique users with detailed actions: {unique_users}<br/>
        • Unique action types: {unique_actions}<br/>
        • Total detailed week actions: {total_det_week}<br/>
        • Total detailed month actions: {total_det_month}<br/>
        """
        elements.append(Paragraph(detailed_summary_text, styles['Normal']))
    else:
        elements.append(Paragraph("No detailed user activity data found for the specified period.", styles['Normal']))

    # ------------------------------------------------------------------
    # SECTION 7: Action Summary Report
    # ------------------------------------------------------------------
    elements.append(Spacer(1, 25))
    section7_title = Paragraph("7. Action Summary Report", section_title_style)
    elements.append(section7_title)

    if action_summary_data:
        summary_table_data = [['Action', 'Comment', 'Week Total', 'Month Total']]
        for row in action_summary_data:
            comment_raw = str(row[1]) if row[1] else ''
            comment_trunc = comment_raw[:40] + ('...' if len(comment_raw) > 40 else '')
            summary_table_data.append([
                str(row[0]) if row[0] else '',
                comment_trunc,
                str(row[2]),
                str(row[3]),
            ])

        summary_table = Table(
            summary_table_data,
            colWidths=[1.5 * inch, 2.5 * inch, 1.2 * inch, 1.2 * inch]
        )
        summary_table.setStyle(TableStyle([
            ('BACKGROUND',  (0, 0), (-1, 0), colors.darkred),
            ('TEXTCOLOR',   (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN',       (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME',    (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE',    (0, 0), (-1, 0), 10),
            ('FONTNAME',    (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE',    (0, 1), (-1, -1), 8),
            ('GRID',        (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN',      (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        elements.append(summary_table)

        elements.append(Spacer(1, 15))
        total_action_types  = len(action_summary_data)
        total_summary_week  = sum(row[2] for row in action_summary_data)
        total_summary_month = sum(row[3] for row in action_summary_data)
        most_popular_week   = max(action_summary_data, key=lambda x: x[2]) if action_summary_data else None
        most_popular_month  = max(action_summary_data, key=lambda x: x[3]) if action_summary_data else None

        action_summary_text = f"""
        <b>Action Summary Statistics:</b><br/>
        • Total unique action types: {total_action_types}<br/>
        • Total actions this week: {total_summary_week}<br/>
        • Total actions this month: {total_summary_month}<br/>
        """
        if most_popular_week:
            action_summary_text += f"• Most popular action (week): {most_popular_week[0]} ({most_popular_week[2]} times)<br/>"
        if most_popular_month:
            action_summary_text += f"• Most popular action (month): {most_popular_month[0]} ({most_popular_month[3]} times)<br/>"

        elements.append(Paragraph(action_summary_text, styles['Normal']))
    else:
        elements.append(Paragraph("No action summary data found for the specified period.", styles['Normal']))

    # ------------------------------------------------------------------
    # SECTION 8: Overall Summary
    # ------------------------------------------------------------------
    elements.append(Spacer(1, 25))
    overall_title = Paragraph("8. Overall Summary", section_title_style)
    elements.append(overall_title)

    overall_summary_parts = []

    if mau_data and len(mau_data) > 0:
        total_mau_val = mau_data[0][2]
        overall_summary_parts.append(f"• MAU total (≈ Telegram): {total_mau_val}")

    if start_only_count is not None:
        overall_summary_parts.append(f"• Start-only пользователи (без действий): {start_only_count}")

    if user_status_data and len(user_status_data) > 0:
        engaged = user_status_data[0][2]
        overall_summary_parts.append(f"• Engaged users (с действиями, 30d): {engaged}")
        if mau_data and mau_data[0][2] > 0:
            conv = round(engaged / mau_data[0][2] * 100, 1)
            overall_summary_parts.append(f"• Конверсия Start → Action: {conv}%")

    if blocked_users_data and len(blocked_users_data) > 2:
        overall_summary_parts.append(f"• Заблокировали бота за месяц: {blocked_users_data[2][1]}")

    if activity_data:
        overall_summary_parts.append(f"• Пользователей с действиями: {len(activity_data)}")

    if daily_data:
        avg_daily = round(sum(row[1] for row in daily_data) / len(daily_data), 1)
        overall_summary_parts.append(f"• Среднее DAU (30 дней): {avg_daily}")

    if action_summary_data:
        overall_summary_parts.append(f"• Уникальных типов действий: {len(action_summary_data)}")

    if overall_summary_parts:
        overall_summary_text = "<b>Key Insights:</b><br/>" + "<br/>".join(overall_summary_parts)
        elements.append(Paragraph(overall_summary_text, styles['Normal']))

    doc.build(elements)
    print(f"PDF report created: {filename}")


async def get_metrics(pool):
    pool_base, pool_log = pool
    vUserID = 372671079
    userID = vUserID

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Running get_metrics()")

    try:
        # QUERY 1: User status overview (engaged users — из t_user_status)
        status_query = '''
            SELECT
                COUNT(*) FILTER (WHERE c_last_active >= NOW() - INTERVAL '1 day')  AS day_count,
                COUNT(*) FILTER (WHERE c_last_active >= NOW() - INTERVAL '7 days')  AS week_count,
                COUNT(*) FILTER (WHERE c_last_active >= NOW() - INTERVAL '30 days') AS month_count
            FROM t_user_status;
        '''
        status_data = await pgDB.fExec_SelectQuery(pool_base, status_query)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Status query: {len(status_data) if status_data else 0} records")

        # QUERY 2: MAU из t_log — все уникальные пользователи (≈ Telegram MAU)
        mau_query = '''
            SELECT
                COUNT(DISTINCT c_log_user_id) FILTER (WHERE c_log_date >= NOW() - INTERVAL '1 day')  AS day_count,
                COUNT(DISTINCT c_log_user_id) FILTER (WHERE c_log_date >= NOW() - INTERVAL '7 days')  AS week_count,
                COUNT(DISTINCT c_log_user_id) FILTER (WHERE c_log_date >= NOW() - INTERVAL '30 days') AS month_count
            FROM t_log
            WHERE c_log_user_id IS NOT NULL;
        '''
        mau_data = await pgDB.fExec_SelectQuery(pool_log, mau_query)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] MAU query: {mau_data[0] if mau_data else 'no data'}")

        # QUERY 3: Start-only — считаем в Python, т.к. t_log и t_user_status в разных БД

        # Получаем ID engaged-пользователей из pool_base
        engaged_ids_query = '''
            SELECT c_user_id
            FROM t_user_status
            WHERE c_last_active >= NOW() - INTERVAL '30 days';
        '''
        engaged_ids_result = await pgDB.fExec_SelectQuery(pool_base, engaged_ids_query)
        engaged_ids = set(row[0] for row in engaged_ids_result) if engaged_ids_result else set()

        # Получаем все MAU ID из pool_log
        mau_ids_query = '''
            SELECT DISTINCT c_log_user_id
            FROM t_log
            WHERE c_log_date >= NOW() - INTERVAL '30 days'
              AND c_log_user_id IS NOT NULL;
        '''
        mau_ids_result = await pgDB.fExec_SelectQuery(pool_log, mau_ids_query)
        mau_ids = set(row[0] for row in mau_ids_result) if mau_ids_result else set()

        # Start-only = в MAU, но не в engaged
        start_only_count = len(mau_ids - engaged_ids)
        print(
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] MAU ids: {len(mau_ids)}, Engaged ids: {len(engaged_ids)}, Start-only: {start_only_count}")

        # QUERY 3b: SpeakPal users — записи где c_log4 = 1
        speakpal_query = '''
            SELECT COUNT(DISTINCT c_log_user_id)
            FROM t_log
            WHERE c_log4 = '1'
              AND c_log_date >= NOW() - INTERVAL '30 days'
              AND c_log_user_id IS NOT NULL;
        '''
        speakpal_result = await pgDB.fExec_SelectQuery(pool_log, speakpal_query)
        speakpal_count = speakpal_result[0][0] if speakpal_result else 0
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SpeakPal users: {speakpal_count}")


        # QUERY 4: Daily activity calendar
        daily_query = '''
            WITH days AS (
                SELECT generate_series::date AS day
                FROM generate_series(
                    date_trunc('day', NOW()) - INTERVAL '29 days',
                    date_trunc('day', NOW()),
                    INTERVAL '1 day'
                )
            )
            SELECT
                d.day,
                COUNT(u.c_user_id) AS num_users
            FROM days d
            LEFT JOIN t_user_status u
                ON u.c_last_active::date = d.day
            GROUP BY d.day
            ORDER BY d.day;
        '''
        daily_data = await pgDB.fExec_SelectQuery(pool_base, daily_query)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Daily query: {len(daily_data) if daily_data else 0} records")

        # QUERY 4b: Daily unique users из t_log (для недельной агрегации)
        daily_log_query = '''
            WITH days AS (
                SELECT generate_series::date AS day
                FROM generate_series(
                    date_trunc('day', NOW()) - INTERVAL '29 days',
                    date_trunc('day', NOW()),
                    INTERVAL '1 day'
                )
            )
            SELECT
                d.day,
                COUNT(DISTINCT l.c_log_user_id) AS num_users
            FROM days d
            LEFT JOIN t_log l
                ON l.c_log_date::date = d.day
                AND l.c_log_user_id IS NOT NULL
            GROUP BY d.day
            ORDER BY d.day;
        '''
        daily_log_data = await pgDB.fExec_SelectQuery(pool_log, daily_log_query)
        print(
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Daily log query: {len(daily_log_data) if daily_log_data else 0} records")

        # QUERY 5: User actions breakdown
        activity_query = '''
            SELECT c_log_user_id AS user_id,
                COUNT(*) FILTER (WHERE c_log_date >= NOW() - INTERVAL '7 days')  AS week_actions,
                COUNT(*) FILTER (WHERE c_log_date >= NOW() - INTERVAL '30 days') AS month_actions
            FROM t_log
            WHERE c_log_type = 5
            GROUP BY c_log_user_id
            HAVING COUNT(*) FILTER (WHERE c_log_date >= NOW() - INTERVAL '30 days') > 0
            ORDER BY c_log_user_id;
        '''
        activity_data = await pgDB.fExec_SelectQuery(pool_log, activity_query)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Activity query: {len(activity_data) if activity_data else 0} records")

        # QUERY 6: Detailed user actions
        detailed_activity_query = '''
            SELECT
                c_log_user_id AS user_id,
                c_log2        AS action,
                c_log_txt     AS comment,
                COUNT(*) FILTER (WHERE c_log_date >= NOW() - INTERVAL '7 days')  AS week_actions,
                COUNT(*) FILTER (WHERE c_log_date >= NOW() - INTERVAL '30 days') AS month_actions
            FROM t_log
            WHERE c_log_type = 5
            GROUP BY c_log_user_id, c_log2, c_log_txt
            HAVING COUNT(*) FILTER (WHERE c_log_date >= NOW() - INTERVAL '30 days') > 0
            ORDER BY c_log_user_id, c_log2, c_log_txt;
        '''
        detailed_activity_data = await pgDB.fExec_SelectQuery(pool_log, detailed_activity_query)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Detailed activity query: {len(detailed_activity_data) if detailed_activity_data else 0} records")

        # QUERY 7: Action summary
        action_summary_query = '''
            SELECT
                c_log2    AS action,
                c_log_txt AS comment,
                COUNT(*) FILTER (WHERE c_log_date >= NOW() - INTERVAL '7 days')  AS week,
                COUNT(*) FILTER (WHERE c_log_date >= NOW() - INTERVAL '30 days') AS month
            FROM t_log
            WHERE c_log_type = 5
            GROUP BY c_log2, c_log_txt
            HAVING COUNT(*) FILTER (WHERE c_log_date >= NOW() - INTERVAL '30 days') > 0
            ORDER BY c_log2, c_log_txt;
        '''
        action_summary_data = await pgDB.fExec_SelectQuery(pool_log, action_summary_query)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Action summary query: {len(action_summary_data) if action_summary_data else 0} records")

        # QUERY 8: Blocked users report
        blocked_users_query = '''
            SELECT 
                'Today' as period,
                COUNT(DISTINCT c_log_user_id) as blocked_users_count,
                1 as sort_order
            FROM public.t_log
            WHERE c_log_type = 1 
              AND LOWER(c_log_txt) LIKE '%blocked%'
              AND c_log_user_id IS NOT NULL
              AND c_log_date::date = CURRENT_DATE

            UNION ALL

            SELECT 
                'Last 7 Days' as period,
                COUNT(DISTINCT c_log_user_id) as blocked_users_count,
                2 as sort_order
            FROM public.t_log
            WHERE c_log_type = 1 
              AND LOWER(c_log_txt) LIKE '%blocked%'
              AND c_log_user_id IS NOT NULL
              AND c_log_date >= CURRENT_DATE - INTERVAL '7 days'

            UNION ALL

            SELECT 
                'Last 30 Days' as period,
                COUNT(DISTINCT c_log_user_id) as blocked_users_count,
                3 as sort_order
            FROM public.t_log
            WHERE c_log_type = 1 
              AND LOWER(c_log_txt) LIKE '%blocked%'
              AND c_log_user_id IS NOT NULL
              AND c_log_date >= CURRENT_DATE - INTERVAL '30 days'

            ORDER BY sort_order;
        '''
        blocked_users_data = await pgDB.fExec_SelectQuery(pool_log, blocked_users_query)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Blocked users query: {len(blocked_users_data) if blocked_users_data else 0} records")

        # ---- Create PDF -------------------------------------------------------
        timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename= f"user_activity_report_{timestamp}.pdf"
        temp_dir    = tempfile.gettempdir()
        pdf_path    = os.path.join(temp_dir, pdf_filename)

        create_pdf_report(
            status_data, daily_data, activity_data, detailed_activity_data,
            action_summary_data, blocked_users_data,
            mau_data, start_only_count,          # новые параметры
            pdf_path, speakpal_count
        )

        # ---- Собираем цифры для caption --------------------------------------
        activity_count   = len(activity_data)    if activity_data    else 0
        detailed_count   = len(detailed_activity_data) if detailed_activity_data else 0
        action_types_count = len(action_summary_data) if action_summary_data else 0
        avg_daily        = round(sum(row[1] for row in daily_data) / len(daily_data), 1) if daily_data else 0

        # Агрегация по неделям из t_log
        weekly_agg = aggregate_weekly(daily_log_data) if daily_log_data else {}

        # DAU / WAU из t_log
        dau_log = mau_data[0][0] if mau_data else 0
        wau_log = mau_data[0][1] if mau_data else 0
        avg_daily_log = round(
            sum(row[1] for row in daily_log_data) / len(daily_log_data), 1
        ) if daily_log_data else 0

        weekly_lines = '\n'.join(
            f'  {label}: {cnt}' for label, cnt in weekly_agg.items()
        )

        total_mau_val    = mau_data[0][2]        if mau_data    else 0
        engaged_users    = status_data[0][2]     if status_data else 0
        conversion_pct   = round(engaged_users / total_mau_val * 100, 1) if total_mau_val > 0 else 0

        blocked_today = blocked_users_data[0][1] if blocked_users_data and len(blocked_users_data) > 0 else 0
        blocked_week  = blocked_users_data[1][1] if blocked_users_data and len(blocked_users_data) > 1 else 0
        blocked_month = blocked_users_data[2][1] if blocked_users_data and len(blocked_users_data) > 2 else 0

        caption = f"""📊 <b>User Activity Report</b>
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🎯 <b>Воронка (30 дней):</b>
• MAU total (≈ Telegram):  {total_mau_val}
  ├ Start-only:            {start_only_count}
  └ Engaged (с действиями):{engaged_users}
• Конверсия Engaged/MAU:  {conversion_pct}%

• Активность speakpal:        {speakpal_count}


📅 <b>Активность (t_log, уник. users):</b>
- DAU (сегодня):  {dau_log}
- WAU (7д, uniq): {wau_log}
- Avg DAU (30д):  {avg_daily_log}
- Action records: {detailed_count}
- Action types:   {action_types_count}

📆 <b>По неделям (все users/день, t_log):</b>
{weekly_lines}

🚫 <b>Blocked Users:</b>
• Today:      {blocked_today}
• This week:  {blocked_week}
• This month: {blocked_month}"""

        # ---- Отправляем PDF --------------------------------------------------
        user_entity = await bot.get_entity(userID)
        await bot.send_file(user_entity, pdf_path, caption=caption, parse_mode='html')
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] PDF sent to user {userID}")

        try:
            os.remove(pdf_path)
        except Exception as cleanup_error:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Warning: cleanup failed: {cleanup_error}")

    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error in get_metrics: {e}")
        try:
            user_entity = await bot.get_entity(userID)
            await bot.send_message(user_entity, f"Error generating report: {str(e)[:200]}...", parse_mode='html')
        except Exception as notify_error:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Could not send error notification: {notify_error}")


async def get_logs():
    """Archive current app.log, clear it, send to Telegram, keep local backup"""
    vUserID = 372671079
    userID  = vUserID

    log_file_path = "app.log"
    timestamp     = datetime.now().strftime("%Y%m%d")

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Running get_logs()")

    try:
        if not os.path.exists(log_file_path):
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Log file not found")
            return

        if os.path.getsize(log_file_path) == 0:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Log file is empty")
            return

        logs_dir = "archived_logs"
        os.makedirs(logs_dir, exist_ok=True)

        archived_log_name = f"app_{timestamp}.log"
        archived_log_path = os.path.join(logs_dir, archived_log_name)
        shutil.copy2(log_file_path, archived_log_path)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Archived to {archived_log_path}")

        with open(log_file_path, 'w') as f:
            pass
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Log file cleared")

        temp_dir = tempfile.gettempdir()
        zip_name = f"app_{timestamp}.zip"
        zip_path = os.path.join(temp_dir, zip_name)

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(archived_log_path, archived_log_name)

        zip_size_mb = round(os.path.getsize(zip_path) / (1024 * 1024), 2)

        caption = f"""📁 <b>Log Archive</b>
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📋 <b>Details:</b>
• Archive date: {timestamp}
• File size: {zip_size_mb} MB
• Local backup: {archived_log_path}
• Original log cleared and ready for new entries"""

        user_entity = await bot.get_entity(userID)
        await bot.send_file(user_entity, zip_path, caption=caption, parse_mode='html')
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Log archive sent to user {userID}")

        try:
            os.remove(zip_path)
        except Exception as cleanup_error:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Warning: ZIP cleanup failed: {cleanup_error}")

    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error in get_logs: {e}")
        try:
            user_entity = await bot.get_entity(userID)
            await bot.send_message(user_entity, f"❌ Error archiving logs: {str(e)[:200]}...", parse_mode='html')
        except Exception as notify_error:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Could not send error notification: {notify_error}")


async def scheduler_task(pool):
    """Scheduler: runs immediately on start, then daily at 21:00"""
    first_run = True

    while True:
        try:
            if first_run:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] First execution")
                await get_metrics(pool)
                await get_logs()
                first_run = False
            else:
                await get_metrics(pool)
                await get_logs()

            next_run     = get_next_run_time()
            sleep_seconds= (next_run - datetime.now()).total_seconds()
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Next run: {next_run.strftime('%Y-%m-%d %H:%M:%S')} (sleep {sleep_seconds:.0f}s)")
            await asyncio.sleep(sleep_seconds)

        except ConnectionError as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Connection error: {e}")
            await asyncio.sleep(60)
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Unexpected error: {e}")
            await asyncio.sleep(60)


async def main():
    pool = None
    try:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Initializing database pool...")
        pool = await pgDB.fPool_Init()
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting scheduler...")
        await scheduler_task(pool)
    except Exception as init_error:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Failed to initialize: {init_error}")
    finally:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Cleaning up resources...")
        if pool is not None:
            try:
                await pool.close()
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Database pool closed.")
            except Exception as e:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error closing pool: {e}")


if __name__ == "__main__":
    with bot as bot_client:
        print('------------------------------------------------------')
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Bot started")
        try:
            bot.loop.run_until_complete(main())
        except KeyboardInterrupt:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Bot stopped by user")
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Bot crashed: {e}")
        finally:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Bot shutdown complete")