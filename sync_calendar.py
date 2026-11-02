import os
import logging
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from typing import Optional
import smartsheet
from icalendar import Calendar, Event

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("exam_calendar_sync")

EASTERN_TZ = ZoneInfo("America/New_York")
CALENDAR_FILE_PATH = "/data/calendar/exam-calendar.ics"


def combine_and_parse_datetime(date_val: Optional[str], time_val: Optional[str]) -> Optional[datetime]:
    """Combines separate Smartsheet Date and Time strings into an Eastern-aware datetime object."""
    if not date_val:
        return None

    date_str = str(date_val).split("T")[0].split(" ")[0].strip()

    if time_val:
        time_str = str(time_val).strip()
        for fmt in ("%Y-%m-%d %I:%M %p", "%Y-%m-%d %I:%M%p", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
            try:
                naive_dt = datetime.strptime(f"{date_str} {time_str}", fmt)
                return naive_dt.replace(tzinfo=EASTERN_TZ)
            except ValueError:
                continue

    try:
        naive_date = datetime.strptime(date_str, "%Y-%m-%d")
        return naive_date.replace(tzinfo=EASTERN_TZ)
    except ValueError:
        return None


def generate_ics_from_smartsheet() -> bytes:
    """Queries Smartsheet API, iterates rows, and builds an iCal byte stream."""
    api_token = os.getenv("SMARTSHEET_ACCESS_TOKEN")
    sheet_id = os.getenv("SHEET_ID")

    if not api_token or not sheet_id:
        raise ValueError("SMARTSHEET_ACCESS_TOKEN and SHEET_ID environment variables must be configured.")

    ss_client = smartsheet.Smartsheet(api_token)
    ss_client.errors_as_exceptions(True)

    logger.info(f"Connecting to Smartsheet API for sheet ID: {sheet_id}")
    sheet = ss_client.Sheets.get_sheet(int(sheet_id))

    cal = Calendar()
    cal.add('prodid', '-//OpenShift Exam Calendar Service//EN')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', 'Exam Schedule')
    cal.add('x-wr-timezone', 'America/New_York')

    col_map = {col.id: col.title.strip() for col in sheet.columns}

    events_parsed = 0
    for row in sheet.rows:
        row_dict = {}
        for cell in row.cells:
            col_name = col_map.get(cell.column_id)
            if col_name:
                row_dict[col_name] = cell.value

        summary = row_dict.get("Description") or "Scheduled Exam"
        description = row_dict.get("Internal Description") or ""
        categories = row_dict.get("Categories") or ""
        uid_val = row_dict.get("UID") or f"exam-row-{row.id}@openshift.exam-calendar"

        start_date = row_dict.get("Start Date")
        start_time = row_dict.get("Start Time")
        end_date = row_dict.get("End Date") or start_date
        end_time = row_dict.get("End Time")

        start_dt = combine_and_parse_datetime(start_date, start_time)
        end_dt = combine_and_parse_datetime(end_date, end_time)

        if start_dt:
            event = Event()
            event.add('summary', str(summary))
            event.add('dtstart', start_dt)
            event.add('dtend', end_dt if end_dt else start_dt)
            event.add('dtstamp', datetime.now(timezone.utc))

            if description:
                event.add('description', str(description))
            if categories:
                cat_list = [c.strip() for c in str(categories).replace(";", ",").split(",") if c.strip()]
                event.add('categories', cat_list)

            event.add('uid', str(uid_val))
            cal.add_component(event)
            events_parsed += 1

    logger.info(f"Successfully generated iCal feed with {events_parsed} events.")
    return cal.to_ical()


def run_sync():
    """Generates the feed bytes and writes the output file to disk."""
    ics_bytes = generate_ics_from_smartsheet()
    os.makedirs(os.path.dirname(CALENDAR_FILE_PATH), exist_ok=True)
    with open(CALENDAR_FILE_PATH, "wb") as f:
        f.write(ics_bytes)
    logger.info(f"Calendar sync completed successfully and written to {CALENDAR_FILE_PATH}")


if __name__ == "__main__":
    run_sync()
