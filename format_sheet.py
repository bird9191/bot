import json
from pathlib import Path

import gspread

import storage
from config import (
    GOOGLE_SERVICE_ACCOUNT_FILE,
    GOOGLE_SERVICE_ACCOUNT_JSON,
    GOOGLE_SHEET_ID,
    GOOGLE_SHEET_NAME,
)


STATUS_OPTIONS = [
    "Новая заявка",
    "В работе",
    "Не дозвонились",
    "Записан на консультацию",
    "Отказ",
    "Закрыта",
]

RESULT_OPTIONS = [
    "",
    "Дозвонились",
    "Не дозвонились",
    "Написали в WhatsApp",
    "Записан",
    "Отказ",
    "Перезвонить позже",
]

COLUMN_WIDTHS = {
    0: 145,
    1: 110,
    2: 165,
    3: 130,
    4: 130,
    5: 135,
    6: 140,
    7: 170,
    8: 145,
    9: 165,
    10: 220,
    11: 180,
    12: 75,
    13: 210,
    14: 90,
    15: 180,
    16: 170,
    17: 210,
    18: 150,
    19: 130,
}

STATUS_COLORS = {
    "Новая заявка": {"red": 1.0, "green": 0.93, "blue": 0.62},
    "В работе": {"red": 0.74, "green": 0.87, "blue": 1.0},
    "Не дозвонились": {"red": 1.0, "green": 0.80, "blue": 0.70},
    "Записан на консультацию": {"red": 0.76, "green": 0.93, "blue": 0.78},
    "Отказ": {"red": 0.93, "green": 0.93, "blue": 0.93},
    "Закрыта": {"red": 0.85, "green": 0.85, "blue": 0.85},
}

STATS_SHEET_NAME = "Статистика"


def _credentials() -> dict:
    if GOOGLE_SERVICE_ACCOUNT_JSON:
        return json.loads(GOOGLE_SERVICE_ACCOUNT_JSON)
    if GOOGLE_SERVICE_ACCOUNT_FILE:
        return json.loads(Path(GOOGLE_SERVICE_ACCOUNT_FILE).read_text(encoding="utf-8"))
    raise RuntimeError("Set GOOGLE_SERVICE_ACCOUNT_JSON or GOOGLE_SERVICE_ACCOUNT_FILE.")


def main() -> None:
    client = gspread.service_account_from_dict(_credentials())
    spreadsheet = client.open_by_key(GOOGLE_SHEET_ID)
    worksheet = spreadsheet.worksheet(GOOGLE_SHEET_NAME)
    _format_leads_sheet(spreadsheet, worksheet)
    _format_stats_sheet(spreadsheet)


def _format_leads_sheet(spreadsheet, worksheet) -> None:
    sheet_id = worksheet.id
    headers = storage.FIELDNAMES
    last_col = storage._column_name(len(headers))
    worksheet.update(
        range_name=f"A1:{last_col}1",
        values=[headers],
        value_input_option="USER_ENTERED",
    )

    requests = [
        {
            "updateSheetProperties": {
                "properties": {
                    "sheetId": sheet_id,
                    "gridProperties": {"frozenRowCount": 1},
                },
                "fields": "gridProperties.frozenRowCount",
            }
        },
        {
            "repeatCell": {
                "range": {"sheetId": sheet_id, "startRowIndex": 0, "endRowIndex": 1},
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 0.08, "green": 0.20, "blue": 0.25},
                        "textFormat": {
                            "foregroundColor": {"red": 1, "green": 1, "blue": 1},
                            "bold": True,
                        },
                        "horizontalAlignment": "CENTER",
                        "verticalAlignment": "MIDDLE",
                        "wrapStrategy": "WRAP",
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment,wrapStrategy)",
            }
        },
        {
            "setBasicFilter": {
                "filter": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 0,
                        "startColumnIndex": 0,
                        "endColumnIndex": len(headers),
                    }
                }
            }
        },
        {
            "setDataValidation": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 1,
                    "startColumnIndex": 2,
                    "endColumnIndex": 3,
                },
                "rule": {
                    "condition": {
                        "type": "ONE_OF_LIST",
                        "values": [{"userEnteredValue": value} for value in STATUS_OPTIONS],
                    },
                    "showCustomUi": True,
                    "strict": True,
                },
            }
        },
        {
            "setDataValidation": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 1,
                    "startColumnIndex": 9,
                    "endColumnIndex": 10,
                },
                "rule": {
                    "condition": {
                        "type": "ONE_OF_LIST",
                        "values": [{"userEnteredValue": value} for value in RESULT_OPTIONS],
                    },
                    "showCustomUi": True,
                    "strict": False,
                },
            }
        },
    ]

    for column_index, width in COLUMN_WIDTHS.items():
        requests.append(
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": sheet_id,
                        "dimension": "COLUMNS",
                        "startIndex": column_index,
                        "endIndex": column_index + 1,
                    },
                    "properties": {"pixelSize": width},
                    "fields": "pixelSize",
                }
            }
        )

    for status, color in STATUS_COLORS.items():
        requests.append(
            {
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [
                            {
                                "sheetId": sheet_id,
                                "startRowIndex": 1,
                                "startColumnIndex": 0,
                                "endColumnIndex": len(headers),
                            }
                        ],
                        "booleanRule": {
                            "condition": {
                                "type": "CUSTOM_FORMULA",
                                "values": [{"userEnteredValue": f'=$C2="{status}"'}],
                            },
                            "format": {"backgroundColor": color},
                        },
                    },
                    "index": 0,
                }
            }
        )

    requests.append(
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": len(headers),
                },
                "cell": {
                    "userEnteredFormat": {
                        "verticalAlignment": "MIDDLE",
                        "wrapStrategy": "WRAP",
                    }
                },
                "fields": "userEnteredFormat(verticalAlignment,wrapStrategy)",
            }
        }
    )

    spreadsheet.batch_update({"requests": requests})


def _format_stats_sheet(spreadsheet) -> None:
    try:
        worksheet = spreadsheet.worksheet(STATS_SHEET_NAME)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=STATS_SHEET_NAME, rows=100, cols=8)

    worksheet.clear()
    worksheet.update(
        range_name="A1:D18",
        values=[
            ["Clean Clinic — статистика заявок", "", "", ""],
            ["Показатель", "Значение", "Цель", "Комментарий"],
            ["Всего заявок", "=COUNTA('Лиды'!A2:A)", "", "Все заявки из листа «Лиды»"],
            ["Новые заявки", '=COUNTIF(\'Лиды\'!C2:C;"Новая заявка")', "", ""],
            ["В работе", '=COUNTIF(\'Лиды\'!C2:C;"В работе")', "", ""],
            ["Не дозвонились", '=COUNTIF(\'Лиды\'!C2:C;"Не дозвонились")', "", ""],
            ["Записаны на консультацию", '=COUNTIF(\'Лиды\'!C2:C;"Записан на консультацию")', "", ""],
            ["Отказы", '=COUNTIF(\'Лиды\'!C2:C;"Отказ")', "", ""],
            ["Закрыты", '=COUNTIF(\'Лиды\'!C2:C;"Закрыта")', "", ""],
            ["Конверсия в запись", '=IFERROR(B7/B3;0)', "30%", "Записи / все заявки"],
            ["Средний балл теста", "=IFERROR(AVERAGE('Лиды'!M2:M);0)", "", ""],
            ["Средняя энергия, %", "=IFERROR(AVERAGE('Лиды'!O2:O);0)", "", ""],
            ["", "", "", ""],
            ["Заявки по дням", "", "", ""],
            ["Дата", "Заявки", "", ""],
            ["=SORT(UNIQUE(FILTER(DATEVALUE(LEFT('Лиды'!A2:A;10));'Лиды'!A2:A<>\"\")))", '=ARRAYFORMULA(IF(A16:A="";;COUNTIF(ARRAYFORMULA(DATEVALUE(LEFT(\'Лиды\'!A2:A;10)));A16:A)))', "", ""],
        ],
        value_input_option="USER_ENTERED",
    )

    sheet_id = worksheet.id
    requests = [
        {
            "mergeCells": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": 4,
                },
                "mergeType": "MERGE_ALL",
            }
        },
        {
            "repeatCell": {
                "range": {"sheetId": sheet_id, "startRowIndex": 0, "endRowIndex": 1},
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 0.08, "green": 0.20, "blue": 0.25},
                        "textFormat": {
                            "foregroundColor": {"red": 1, "green": 1, "blue": 1},
                            "bold": True,
                            "fontSize": 14,
                        },
                        "horizontalAlignment": "CENTER",
                        "verticalAlignment": "MIDDLE",
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)",
            }
        },
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 1,
                    "endRowIndex": 2,
                    "startColumnIndex": 0,
                    "endColumnIndex": 4,
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 0.88, "green": 0.93, "blue": 0.95},
                        "textFormat": {"bold": True},
                        "horizontalAlignment": "CENTER",
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)",
            }
        },
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 13,
                    "endRowIndex": 15,
                    "startColumnIndex": 0,
                    "endColumnIndex": 2,
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 0.88, "green": 0.93, "blue": 0.95},
                        "textFormat": {"bold": True},
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat)",
            }
        },
        {
            "repeatCell": {
                "range": {"sheetId": sheet_id, "startRowIndex": 9, "endRowIndex": 10, "startColumnIndex": 1, "endColumnIndex": 3},
                "cell": {"userEnteredFormat": {"numberFormat": {"type": "PERCENT", "pattern": "0.0%"}}},
                "fields": "userEnteredFormat.numberFormat",
            }
        },
        {
            "repeatCell": {
                "range": {"sheetId": sheet_id, "startRowIndex": 15, "startColumnIndex": 0, "endColumnIndex": 1},
                "cell": {"userEnteredFormat": {"numberFormat": {"type": "DATE", "pattern": "dd.mm.yyyy"}}},
                "fields": "userEnteredFormat.numberFormat",
            }
        },
        {
            "updateSheetProperties": {
                "properties": {"sheetId": sheet_id, "gridProperties": {"frozenRowCount": 2}},
                "fields": "gridProperties.frozenRowCount",
            }
        },
    ]

    for column_index, width in {0: 230, 1: 120, 2: 100, 3: 260}.items():
        requests.append(
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": sheet_id,
                        "dimension": "COLUMNS",
                        "startIndex": column_index,
                        "endIndex": column_index + 1,
                    },
                    "properties": {"pixelSize": width},
                    "fields": "pixelSize",
                }
            }
        )

    spreadsheet.batch_update({"requests": requests})


if __name__ == "__main__":
    main()
