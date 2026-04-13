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
        # If it's already past 21:00, schedule for tomorrow at 21:00
        tomorrow_21 = today_21 + timedelta(days=1)
        return tomorrow_21


def create_daily_calendar_table(daily_data):
    """Create a weekly calendar table from daily data"""
    # Create a dictionary for quick lookup
    daily_dict = {row[0]: row[1] for row in daily_data} if daily_data else {}

    # Start from the earliest date (30 days ago)
    start_date = datetime.now().date() - timedelta(days=29)

    # Create calendar structure
    calendar_data = [['Week', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']]

    current_date = start_date
    week_num = 1
    week_row = [f'Week {week_num}']

    # Find the Monday of the first week (may be before our start_date)
    days_since_monday = current_date.weekday()
    week_start = current_date - timedelta(days=days_since_monday)

    for day_offset in range(7 * 5):  # Up to 5 weeks to cover 30 days
        cal_date = week_start + timedelta(days=day_offset)

        if day_offset > 0 and day_offset % 7 == 0:
            # Start new week
            calendar_data.append(week_row)
            week_num += 1
            week_row = [f'Week {week_num}']

        if cal_date < start_date or cal_date > datetime.now().date():
            # Outside our data range
            week_row.append('-')
        else:
            # Within our data range
            user_count = daily_dict.get(cal_date, 0)
            week_row.append(str(user_count))

    # Add the last week if it has data
    if len(week_row) > 1:
        # Pad the last week if needed
        while len(week_row) < 8:
            week_row.append('-')
        calendar_data.append(week_row)

    return calendar_data


def create_pdf_report(user_status_data, daily_data, activity_data, detailed_activity_data, action_summary_data,
                      filename):
    """Create a PDF report with user metrics tables"""
    doc = SimpleDocTemplate(filename, pagesize=A4)
    elements = []

    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1,  # Center alignment
    )

    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=15,
        spaceBefore=20,
        alignment=0,  # Left alignment
    )

    # Add main title
    title = Paragraph("User Activity Report", title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))

    # Add generation date
    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=1,  # Center alignment
    )
    date_text = Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", date_style)
    elements.append(date_text)
    elements.append(Spacer(1, 20))

    # SECTION 1: User Status Report (moved to first)
    section1_title = Paragraph("1. Active Users Overview", section_title_style)
    elements.append(section1_title)

    if user_status_data and len(user_status_data) > 0:
        status_row = user_status_data[0]  # Should be only one row

        # Create status overview table
        status_table_data = [
            ['Period', 'Active Users Count'],
            ['Last 24 Hours', str(status_row[0])],  # day_count
            ['Last 7 Days', str(status_row[1])],  # week_count
            ['Last 30 Days', str(status_row[2])]  # month_count
        ]

        status_table = Table(status_table_data, colWidths=[3 * inch, 3 * inch])

        # Style the status table
        status_table.setStyle(TableStyle([
            # Header row styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),

            # Data rows styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),

            # Grid
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

            # Alternating row colors for data
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.lightcyan, colors.lightblue]),
        ]))

        elements.append(status_table)

        # Status summary
        elements.append(Spacer(1, 15))
        status_summary_text = f"""
        <b>Status Summary:</b><br/>
        • Daily Active Users: {status_row[0]}<br/>
        • Weekly Active Users: {status_row[1]}<br/>
        • Monthly Active Users: {status_row[2]}<br/>
        """
        status_summary = Paragraph(status_summary_text, styles['Normal'])
        elements.append(status_summary)

    else:
        no_status_text = Paragraph("No user status data found.", styles['Normal'])
        elements.append(no_status_text)

    # SECTION 2: Daily Activity Calendar (new section)
    elements.append(Spacer(1, 25))
    section2_title = Paragraph("2. Daily Activity Calendar (Last 30 Days)", section_title_style)
    elements.append(section2_title)

    if daily_data:
        calendar_table_data = create_daily_calendar_table(daily_data)

        # Create calendar table
        calendar_table = Table(calendar_table_data,
                               colWidths=[0.8 * inch, 0.8 * inch, 0.8 * inch, 0.8 * inch, 0.8 * inch, 0.8 * inch,
                                          0.8 * inch, 0.8 * inch])

        # Style the calendar table
        calendar_table.setStyle(TableStyle([
            # Header row styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),

            # Week column styling
            ('BACKGROUND', (0, 1), (0, -1), colors.lightgreen),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (0, -1), 9),

            # Data cells styling
            ('BACKGROUND', (1, 1), (-1, -1), colors.white),
            ('FONTNAME', (1, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (1, 1), (-1, -1), 8),

            # Grid
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

            # Weekend styling (Saturday and Sunday)
            ('BACKGROUND', (6, 0), (6, 0), colors.green),  # Saturday header
            ('BACKGROUND', (7, 0), (7, 0), colors.green),  # Sunday header
            ('BACKGROUND', (6, 1), (6, -1), colors.lightgrey),  # Saturday data
            ('BACKGROUND', (7, 1), (7, -1), colors.lightgrey),  # Sunday data
        ]))

        elements.append(calendar_table)

        # Calendar summary
        elements.append(Spacer(1, 15))
        total_daily_users = sum(row[1] for row in daily_data) if daily_data else 0
        avg_daily_users = round(total_daily_users / len(daily_data), 1) if daily_data else 0
        max_daily_users = max(row[1] for row in daily_data) if daily_data else 0
        min_daily_users = min(row[1] for row in daily_data) if daily_data else 0

        calendar_summary_text = f"""
        <b>Calendar Summary:</b><br/>
        • Average daily active users: {avg_daily_users}<br/>
        • Peak daily active users: {max_daily_users}<br/>
        • Minimum daily active users: {min_daily_users}<br/>
        • Total user-days: {total_daily_users}<br/>
        """
        calendar_summary = Paragraph(calendar_summary_text, styles['Normal'])
        elements.append(calendar_summary)

    else:
        no_calendar_text = Paragraph("No daily activity data found.", styles['Normal'])
        elements.append(no_calendar_text)

    # SECTION 3: User Actions Report (moved to third)
    elements.append(Spacer(1, 25))
    section3_title = Paragraph("3. User Actions Breakdown", section_title_style)
    elements.append(section3_title)

    if activity_data:
        # Table headers for activity data
        table_data = [['User ID', 'Week Actions', 'Month Actions']]

        # Add data rows
        for row in activity_data:
            table_data.append([
                str(row[0]),  # user_id
                str(row[1]),  # week_actions
                str(row[2])  # month_actions
            ])

        # Create activity table
        activity_table = Table(table_data, colWidths=[2 * inch, 2 * inch, 2 * inch])

        # Style the activity table
        activity_table.setStyle(TableStyle([
            # Header row styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),

            # Data rows styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),

            # Grid
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))

        elements.append(activity_table)

        # Activity summary
        elements.append(Spacer(1, 15))
        total_users = len(activity_data)
        total_week_actions = sum(row[1] for row in activity_data)
        total_month_actions = sum(row[2] for row in activity_data)

        activity_summary_text = f"""
        <b>Actions Summary:</b><br/>
        • Active Users with Actions: {total_users}<br/>
        • Total Week Actions: {total_week_actions}<br/>
        • Total Month Actions: {total_month_actions}<br/>
        """
        activity_summary = Paragraph(activity_summary_text, styles['Normal'])
        elements.append(activity_summary)
    else:
        no_activity_text = Paragraph("No user activity data found for the specified period.", styles['Normal'])
        elements.append(no_activity_text)

    # SECTION 4: Detailed User Actions Report (NEW)
    elements.append(Spacer(1, 25))
    section4_title = Paragraph("4. Detailed User Actions Report", section_title_style)
    elements.append(section4_title)

    if detailed_activity_data:
        # Table headers for detailed activity data
        detailed_table_data = [['User ID', 'Action', 'Comment', 'Week Count', 'Month Count']]

        # Add data rows
        for row in detailed_activity_data:
            detailed_table_data.append([
                str(row[0]),  # user_id
                str(row[1]) if row[1] else '',  # action
                str(row[2])[:30] + ('...' if len(str(row[2])) > 30 else '') if row[2] else '',  # comment (truncated)
                str(row[3]),  # week_actions
                str(row[4])  # month_actions
            ])

        # Create detailed activity table
        detailed_activity_table = Table(detailed_table_data,
                                        colWidths=[1.2 * inch, 1.2 * inch, 2.2 * inch, 1 * inch, 1 * inch])

        # Style the detailed activity table
        detailed_activity_table.setStyle(TableStyle([
            # Header row styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.purple),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),

            # Data rows styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.lavender),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),

            # Grid
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))

        elements.append(detailed_activity_table)

        # Detailed activity summary
        elements.append(Spacer(1, 15))
        total_detailed_records = len(detailed_activity_data)
        unique_users = len(set(row[0] for row in detailed_activity_data))
        unique_actions = len(set(row[1] for row in detailed_activity_data if row[1]))
        total_detailed_week = sum(row[3] for row in detailed_activity_data)
        total_detailed_month = sum(row[4] for row in detailed_activity_data)

        detailed_summary_text = f"""
        <b>Detailed Actions Summary:</b><br/>
        • Total action records: {total_detailed_records}<br/>
        • Unique users with detailed actions: {unique_users}<br/>
        • Unique action types: {unique_actions}<br/>
        • Total detailed week actions: {total_detailed_week}<br/>
        • Total detailed month actions: {total_detailed_month}<br/>
        """
        detailed_summary = Paragraph(detailed_summary_text, styles['Normal'])
        elements.append(detailed_summary)
    else:
        no_detailed_text = Paragraph("No detailed user activity data found for the specified period.", styles['Normal'])
        elements.append(no_detailed_text)

    # SECTION 5: Action Summary Report (NEW)
    elements.append(Spacer(1, 25))
    section5_title = Paragraph("5. Action Summary Report", section_title_style)
    elements.append(section5_title)

    if action_summary_data:
        # Table headers for action summary data
        summary_table_data = [['Action', 'Comment', 'Week Total', 'Month Total']]

        # Add data rows
        for row in action_summary_data:
            summary_table_data.append([
                str(row[0]) if row[0] else '',  # action
                str(row[1])[:40] + ('...' if len(str(row[1])) > 40 else '') if row[1] else '',  # comment (truncated)
                str(row[2]),  # week_count
                str(row[3])  # month_count
            ])

        # Create action summary table
        summary_table = Table(summary_table_data,
                              colWidths=[1.5 * inch, 2.5 * inch, 1.2 * inch, 1.2 * inch])

        # Style the action summary table
        summary_table.setStyle(TableStyle([
            # Header row styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),

            # Data rows styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.mistyrose),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),

            # Grid
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))

        elements.append(summary_table)

        # Action summary statistics
        elements.append(Spacer(1, 15))
        total_action_types = len(action_summary_data)
        total_summary_week = sum(row[2] for row in action_summary_data)
        total_summary_month = sum(row[3] for row in action_summary_data)
        most_popular_week = max(action_summary_data, key=lambda x: x[2]) if action_summary_data else None
        most_popular_month = max(action_summary_data, key=lambda x: x[3]) if action_summary_data else None

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

        action_summary_paragraph = Paragraph(action_summary_text, styles['Normal'])
        elements.append(action_summary_paragraph)
    else:
        no_summary_text = Paragraph("No action summary data found for the specified period.", styles['Normal'])
        elements.append(no_summary_text)

    # OVERALL SUMMARY (Updated to include new sections)
    elements.append(Spacer(1, 25))
    overall_title = Paragraph("6. Overall Summary", section_title_style)
    elements.append(overall_title)

    # Calculate some interesting metrics
    overall_summary_parts = []

    if user_status_data and len(user_status_data) > 0:
        status_row = user_status_data[0]
        overall_summary_parts.append(f"• Total registered users (active in 30 days): {status_row[2]}")

    if activity_data:
        users_with_actions = len(activity_data)
        overall_summary_parts.append(f"• Users with recorded actions: {users_with_actions}")

        if user_status_data and len(user_status_data) > 0:
            status_row = user_status_data[0]
            engagement_rate = round((len(activity_data) / status_row[2] * 100), 1) if status_row[2] > 0 else 0
            overall_summary_parts.append(
                f"• User engagement rate: {engagement_rate}% (users with actions / total active users)")

    if daily_data:
        avg_daily = round(sum(row[1] for row in daily_data) / len(daily_data), 1)
        overall_summary_parts.append(f"• Average daily active users (30 days): {avg_daily}")

    if detailed_activity_data:
        total_detailed_records = len(detailed_activity_data)
        overall_summary_parts.append(f"• Total detailed action records: {total_detailed_records}")

    if action_summary_data:
        total_action_types = len(action_summary_data)
        overall_summary_parts.append(f"• Unique action types tracked: {total_action_types}")

    if overall_summary_parts:
        overall_summary_text = "<b>Key Insights:</b><br/>" + "<br/>".join(overall_summary_parts)
        overall_summary = Paragraph(overall_summary_text, styles['Normal'])
        elements.append(overall_summary)

    # Build PDF
    doc.build(elements)
    print(f"PDF report created: {filename}")


async def get_metrics(pool):
    pool_base, pool_log = pool
    vUserID = 372671079
    userID = vUserID

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Running get_metrics()")

    try:
        # QUERY 1: User status overview (active users count)
        status_query = '''
            SELECT
                COUNT(*) FILTER (WHERE c_last_active >= NOW() - INTERVAL '1 day')  AS day_count,
                COUNT(*) FILTER (WHERE c_last_active >= NOW() - INTERVAL '7 days')  AS week_count,
                COUNT(*) FILTER (WHERE c_last_active >= NOW() - INTERVAL '30 days') AS month_count
            FROM t_user_status;
        '''
        status_data = await pgDB.fExec_SelectQuery(pool_base, status_query)
        print(
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Status query executed, found {len(status_data) if status_data else 0} records")

        # QUERY 2: Daily activity calendar (new query)
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
        print(
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Daily query executed, found {len(daily_data) if daily_data else 0} records")

        # QUERY 3: User actions breakdown (за неделю, месяц)
        activity_query = '''
            SELECT c_log_user_id AS user_id,
                COUNT(*) FILTER (WHERE c_log_date >= NOW() - INTERVAL '7 days')  AS week_actions,
                COUNT(*) FILTER (WHERE c_log_date >= NOW() - INTERVAL '30 days') AS month_actions
            FROM
                t_log
            WHERE
                c_log_type = 5
            GROUP BY
                c_log_user_id
            HAVING
                COUNT(*) FILTER (WHERE c_log_date >= NOW() - INTERVAL '30 days') > 0
            ORDER BY
                c_log_user_id;
        '''
        activity_data = await pgDB.fExec_SelectQuery(pool_log, activity_query)
        print(
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Activity query executed, found {len(activity_data) if activity_data else 0} records")

        # QUERY 4: Detailed user actions (NEW)
        detailed_activity_query = '''
            SELECT
                c_log_user_id AS user_id,
                c_log2        AS action,
                c_log_txt     AS comment,
                COUNT(*) FILTER (WHERE c_log_date >= NOW() - INTERVAL '7 days')  AS week_actions,
                COUNT(*) FILTER (WHERE c_log_date >= NOW() - INTERVAL '30 days') AS month_actions
            FROM
                t_log
            WHERE
                c_log_type = 5
            GROUP BY
                c_log_user_id,
                c_log2,
                c_log_txt
            HAVING
                COUNT(*) FILTER (WHERE c_log_date >= NOW() - INTERVAL '30 days') > 0
            ORDER BY
                c_log_user_id,
                c_log2,
                c_log_txt;
        '''
        detailed_activity_data = await pgDB.fExec_SelectQuery(pool_log, detailed_activity_query)
        print(
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Detailed activity query executed, found {len(detailed_activity_data) if detailed_activity_data else 0} records")

        # QUERY 5: Action summary (NEW)
        action_summary_query = '''
            SELECT
                c_log2 AS action,
                c_log_txt AS comment,
                COUNT(*) FILTER (WHERE c_log_date >= NOW() - INTERVAL '7 days') AS week,
                COUNT(*) FILTER (WHERE c_log_date >= NOW() - INTERVAL '30 days') AS month
            FROM
                t_log
            WHERE
                c_log_type = 5
            GROUP BY
                c_log2,
                c_log_txt
            HAVING
                COUNT(*) FILTER (WHERE c_log_date >= NOW() - INTERVAL '30 days') > 0
            ORDER BY
                c_log2,
                c_log_txt;
        '''
        action_summary_data = await pgDB.fExec_SelectQuery(pool_log, action_summary_query)
        print(
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Action summary query executed, found {len(action_summary_data) if action_summary_data else 0} records")

        # Create PDF report with all datasets
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"user_activity_report_{timestamp}.pdf"

        # Create PDF in temporary directory
        temp_dir = tempfile.gettempdir()
        pdf_path = os.path.join(temp_dir, pdf_filename)

        create_pdf_report(status_data, daily_data, activity_data, detailed_activity_data, action_summary_data, pdf_path)

        # Prepare caption with summary info
        activity_count = len(activity_data) if activity_data else 0
        detailed_count = len(detailed_activity_data) if detailed_activity_data else 0
        action_types_count = len(action_summary_data) if action_summary_data else 0
        total_active_month = status_data[0][2] if status_data and len(status_data) > 0 else 0
        avg_daily = round(sum(row[1] for row in daily_data) / len(daily_data), 1) if daily_data else 0

        caption = f"""📊 <b>User Activity Report</b>
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📈 <b>Quick Stats:</b>
• Total active users (30d): {total_active_month}
• Daily active: {status_data[0][0] if status_data and len(status_data) > 0 else 0}
• Weekly active: {status_data[0][1] if status_data and len(status_data) > 0 else 0}
• Avg daily active: {avg_daily}
• Users with actions: {activity_count}
• Detailed action records: {detailed_count}
• Unique action types: {action_types_count}"""

        # Send PDF file to user
        # -----------------------------------------------------------------------------
        user_entity = await bot.get_entity(userID)

        # Send the PDF file
        await bot.send_file(
            user_entity,
            pdf_path,
            caption=caption,
            parse_mode='html'
        )
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] PDF report sent successfully to user {userID}")

        # Clean up temporary file
        try:
            os.remove(pdf_path)
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Temporary file {pdf_filename} cleaned up")
        except Exception as cleanup_error:
            print(
                f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Warning: Could not clean up temporary file: {cleanup_error}")

    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error in get_metrics: {e}")

        # Send error notification to user
        try:
            user_entity = await bot.get_entity(userID)
            error_msg = f"Error generating report: {str(e)[:200]}..."
            await bot.send_message(user_entity, error_msg, parse_mode='html')
        except Exception as notify_error:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Could not send error notification: {notify_error}")


async def get_logs():
    """
    Archive current app.log, clear it, send to Telegram, and keep local backup
    """
    vUserID = 372671079
    userID = vUserID

    log_file_path = "app.log"
    timestamp = datetime.now().strftime("%Y%m%d")

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Running get_logs()")

    try:
        # Check if log file exists
        if not os.path.exists(log_file_path):
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Log file {log_file_path} not found")
            return

        # Check if log file is empty
        if os.path.getsize(log_file_path) == 0:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Log file {log_file_path} is empty")
            return

        # Create logs directory if it doesn't exist
        logs_dir = "archived_logs"
        os.makedirs(logs_dir, exist_ok=True)

        # Step 1: Copy app.log to archived_logs/app_<yyyymmdd>.log
        archived_log_name = f"app_{timestamp}.log"
        archived_log_path = os.path.join(logs_dir, archived_log_name)

        shutil.copy2(log_file_path, archived_log_path)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Log file archived to {archived_log_path}")

        # Step 2: Clear the original app.log file
        with open(log_file_path, 'w') as f:
            pass
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Original log file {log_file_path} cleared")

        # Step 3: Create ZIP file in temp directory
        temp_dir = tempfile.gettempdir()
        zip_name = f"app_{timestamp}.zip"
        zip_path = os.path.join(temp_dir, zip_name)

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(archived_log_path, archived_log_name)

        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ZIP file created: {zip_path}")

        # Get file size for caption
        zip_size_bytes = os.path.getsize(zip_path)
        zip_size_mb = round(zip_size_bytes / (1024 * 1024), 2)

        # Prepare caption
        caption = f"""📁 <b>Log Archive</b>
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📋 <b>Details:</b>
• Archive date: {timestamp}
• File size: {zip_size_mb} MB
• Local backup: {archived_log_path}
• Original log cleared and ready for new entries"""

        # Step 4: Send ZIP file to Telegram
        user_entity = await bot.get_entity(userID)

        await bot.send_file(
            user_entity,
            zip_path,
            caption=caption,
            parse_mode='html'
        )

        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Log archive sent successfully to user {userID}")

        # Step 5: Clean up temporary ZIP file (keep local archived log)
        try:
            os.remove(zip_path)
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Temporary ZIP file cleaned up")
        except Exception as cleanup_error:
            print(
                f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Warning: Could not clean up temporary ZIP: {cleanup_error}")

    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error in get_logs: {e}")

        # Send error notification to user
        try:
            user_entity = await bot.get_entity(userID)
            error_msg = f"❌ Error archiving logs: {str(e)[:200]}..."
            await bot.send_message(user_entity, error_msg, parse_mode='html')
        except Exception as notify_error:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Could not send error notification: {notify_error}")

async def scheduler_task(pool):
    """Scheduler task that runs get_metrics on first run and then daily at 21:00"""
    first_run = True

    while True:
        try:
            if first_run:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Running first execution of get_metrics()")
                await get_metrics(pool)
                await get_logs()
                first_run = False

                # Calculate next run time (21:00 today or tomorrow)
                next_run = get_next_run_time()
                sleep_seconds = (next_run - datetime.now()).total_seconds()

                print(
                    f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Next run scheduled for: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Sleeping for {sleep_seconds:.0f} seconds")

                await asyncio.sleep(sleep_seconds)
            else:
                # Run the metrics function
                await get_metrics(pool)
                await get_logs()


                # Schedule next run for tomorrow at 21:00
                next_run = get_next_run_time()
                sleep_seconds = (next_run - datetime.now()).total_seconds()

                print(
                    f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Next run scheduled for: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Sleeping for {sleep_seconds:.0f} seconds")

                await asyncio.sleep(sleep_seconds)

        except ConnectionError as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Connection error in scheduler: {e}")
            await asyncio.sleep(60)  # Wait 1 minute before retrying
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Unexpected error in scheduler: {e}")
            await asyncio.sleep(60)  # Wait 1 minute before retrying


async def main():
    pool = None

    try:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Initializing database pool...")
        # Initialize the pool
        pool = await pgDB.fPool_Init()  # 2 - prod

        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting scheduler...")

        # Start the scheduler task
        await scheduler_task(pool)

    except Exception as init_error:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Failed to initialize: {init_error}")
    finally:
        # Cleanup resources
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Cleaning up resources...")

        if pool is not None:
            try:
                await pool.close()
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Database pool closed.")
            except Exception as e:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error closing database pool: {e}")


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