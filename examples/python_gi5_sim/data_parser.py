import struct
import json
import os

def load_schema(module_name):
    """讀取單一真理來源 (SSOT)"""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    with open(os.path.join(base_dir, 'definitions', f'{module_name}.json'), 'r') as f:
        return json.load(f)

def parse_uvc_binary(schema, cmd_name, binary_data):
    """解析 USB 60-byte 二進位資料"""
    cmd_def = next((c for c in schema['commands'] if c['name'] == cmd_name), None)
    result = {}
    for field in cmd_def['fields']:
        offset = field['offset']
        if field['type'] == 'uint32':
            result[field['name']] = struct.unpack_from('<I', binary_data, offset)[0]
        # ... 其他型別解析 (略)
    return result

if __name__ == "__main__":
    print("=== gi5_sim Multi-Format Parser ===")
    schema = load_schema('system')

    # 1. 處理 USB 二進位資料
    mock_bin = bytearray(60)
    struct.pack_into('<I', mock_bin, 4, 3600) # 模擬 Uptime 3600 秒
    bin_result = parse_uvc_binary(schema, 'SYSTEM_STATUS', mock_bin)
    print(f"[Parsed from USB .bin] Uptime: {bin_result.get('uptime')} seconds")

    # 2. 處理網路 JSON 資料
    mock_json = '{"cpu_temp": 45, "cpu_usage": 32, "uptime": 3600}'
    json_result = json.loads(mock_json)
    print(f"[Parsed from Network .json] Uptime: {json_result.get('uptime')} seconds")