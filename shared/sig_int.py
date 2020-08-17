import openpyxl
import re

file_sig_int = 'project_files\\Tele2_TMS_Signal_integration_v4.5-draft.xlsx'
wb = openpyxl.load_workbook(file_sig_int, True)


def get_sheets_list(region):
    ws_list = list(filter(lambda i: re.search('^'+region, i), wb.sheetnames))
    return ws_list


def get_gy_peers(w_sheet):
    ws = wb[w_sheet]
    s1_gy = wb.defined_names[f'{w_sheet.lower()}_s1_gy'].attr_text
    rng = s1_gy[s1_gy.find('!') + 1:]
    gy_peers = []
    for row in ws[rng]:
        gy_peers.append({"peerId": row[13].value,
                         "hostName": row[9].value,
                         "port": int(row[11].value),
                         "bindAddress": None,
                         "enabled": True,
                         "watchdogTimeoutMs": 30000
                         })
    # Non-production RTUCG for testing purposes. Disabled by default
    gy_peers.append({"peerId": "T2TST-RTUCG-01-2",
                     "hostName": "10.78.245.57",
                     "port": 3878,
                     "bindAddress": None,
                     "enabled": False,  # True,
                     "watchdogTimeoutMs": 30000
                     })
    return gy_peers
