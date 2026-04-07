#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import argparse
from datetime import datetime

class ProtocolGenerator:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.definitions = {}
        self.load_definitions()

    def load_definitions(self):
        """載入 definitions/ 下所有的中立資料結構定義"""
        def_path = os.path.join(self.base_dir, "definitions")
        for filename in os.listdir(def_path):
            if filename.endswith(".json"):
                with open(os.path.join(def_path, filename), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.definitions[filename] = data

    def _get_c_type(self, t):
        """將 JSON 型別對應至 C 標準型別"""
        mapping = {
            "uint8": "uint8_t", "uint16": "uint16_t", "uint32": "uint32_t",
            "int8": "int8_t", "int16": "int16_t", "int32": "int32_t",
            "string": "char", "char": "char"
        }
        return mapping.get(t, "uint8_t")

    def _get_ts_type(self, t):
        """將 JSON 型別對應至 TypeScript 型別"""
        return "string" if t in ["string", "char"] else "number"

    def generate_uvc_cpp(self, mapping_file):
        """產出 UVC XU 專用二進位結構體 (精確對齊與長度檢查)"""
        with open(mapping_file, 'r', encoding='utf-8') as f:
            mapping = json.load(f)
        
        lines = [
            "/*",
            f" * Auto-generated UVC XU Binary Structures - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            " * DO NOT MODIFY MANUALLY.",
            " */",
            "#ifndef FUP_UVC_STRUCTS_H",
            "#define FUP_UVC_STRUCTS_H",
            "",
            "#include <stdint.h>",
            "#include \"endian_utils.h\"", # 引入跨平台端序轉換
            "",
            "// Cross-Platform Alignment Protection",
            "#if defined(_MSC_VER)",
            "    #define FUP_PACKED_START __pragma(pack(push, 1))",
            "    #define FUP_PACKED_END   __pragma(pack(pop))",
            "#else",
            "    #define FUP_PACKED_START",
            "    #define FUP_PACKED_END   __attribute__((packed))",
            "#endif\n"
        ]

        max_payload = mapping.get("max_payload_size", 60)

        for cmd in mapping['commands']:
            if cmd['definition'] not in self.definitions: continue
            def_data = self.definitions[cmd['definition']]
            cmd_def = next((c for c in def_data['commands'] if c['name'] == cmd['name']), None)
            if not cmd_def: continue

            lines.append(f"// Command ID: {cmd['id']} - {cmd['description']}")
            lines.append("FUP_PACKED_START")
            lines.append(f"typedef struct {{")
            
            curr_offset = 0
            for field in cmd_def['fields']:
                # 1. 處理潛在的記憶體間隙 (Padding)
                if field['offset'] > curr_offset:
                    pad_size = field['offset'] - curr_offset
                    lines.append(f"    uint8_t _res_{curr_offset}[{pad_size}];")
                    curr_offset = field['offset']
                
                # 2. 宣告欄位
                c_type = self._get_c_type(field['type'])
                unit_cmt = f" // Unit: {field['unit']}" if 'unit' in field else ""
                
                if field['type'] in ["string", "char"] and "size" in field:
                    lines.append(f"    {c_type} {field['name']}[{field['size']}];{unit_cmt}")
                    curr_offset += field['size']
                else:
                    lines.append(f"    {c_type} {field['name']};{unit_cmt}")
                    size_map = {"uint8": 1, "int8": 1, "uint16": 2, "int16": 2, "uint32": 4, "int32": 4}
                    curr_offset += size_map.get(field['type'], 1)

            # 3. 尾部補齊至 UVC XU 最大限制
            if curr_offset < max_payload:
                pad_size = max_payload - curr_offset
                lines.append(f"    uint8_t _padding_{curr_offset}[{pad_size}];")
            
            lines.append(f"}} FUP_PACKED_END {cmd['name']}_t;")
            
            # 4. 跨平台安全網：強制編譯器檢查最終大小
            lines.append(f"static_assert(sizeof({cmd['name']}_t) == {max_payload}, \"FUP Error: Struct size != {max_payload}\");\n")

        lines.append("#endif // FUP_UVC_STRUCTS_H")
        return "\n".join(lines)

    def generate_rtsp_qt(self, mapping_file):
        """產出 RTSP/ONVIF 專用的 Qt JSON 序列化/反序列化類別"""
        with open(mapping_file, 'r', encoding='utf-8') as f:
            mapping = json.load(f)

        lines = [
            "/*",
            f" * Auto-generated RTSP/CGI JSON Models for Qt - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            " */",
            "#ifndef FUP_NETWORK_MODELS_H",
            "#define FUP_NETWORK_MODELS_H",
            "",
            "#include <QJsonObject>",
            "#include <QString>",
            ""
        ]

        for cmd in mapping['commands']:
            if cmd['definition'] not in self.definitions: continue
            def_data = self.definitions[cmd['definition']]
            cmd_def = next((c for c in def_data['commands'] if c['name'] == cmd['name']), None)
            if not cmd_def: continue

            lines.append(f"// Endpoint: {cmd['method']} {cmd['endpoint']}")
            lines.append(f"struct {cmd['name']}_Net {{")
            
            # 宣告成員
            for field in cmd_def['fields']:
                q_type = "QString" if field['type'] in ["string", "char"] else "int"
                # 如果是 uint32 等較大數值，建議轉 qint64 以防溢位
                if field['type'] in ["uint32", "int32"]: q_type = "qint64"
                lines.append(f"    {q_type} {field['name']};")

            # 實作 fromJson 解析函數
            lines.append(f"\n    void fromJson(const QJsonObject &obj) {{")
            for field in cmd_def['fields']:
                if field['type'] in ["string", "char"]:
                    lines.append(f"        {field['name']} = obj[\"{field['name']}\"].toString();")
                else:
                    if field['type'] in ["uint32", "int32"]:
                        lines.append(f"        {field['name']} = obj[\"{field['name']}\"].toInteger();")
                    else:
                        lines.append(f"        {field['name']} = obj[\"{field['name']}\"].toInt();")
            lines.append("    }")

            # 實作 toJson 封裝函數 (供 POST/PUT 使用)
            lines.append(f"\n    QJsonObject toJson() const {{")
            lines.append("        QJsonObject obj;")
            for field in cmd_def['fields']:
                lines.append(f"        obj[\"{field['name']}\"] = {field['name']};")
            lines.append("        return obj;")
            lines.append("    }")
            
            lines.append("};\n")

        lines.append("#endif // FUP_NETWORK_MODELS_H")
        return "\n".join(lines)

    def generate_ts(self):
        """為前端 OmniSight-Forge 產出 TypeScript Interfaces"""
        lines = [
            "/**",
            f" * Auto-generated TS Interfaces for FUP - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            " */",
            ""
        ]
        
        for def_name, def_data in self.definitions.items():
            lines.append(f"// --- Module: {def_data.get('module', def_name)} ---")
            for cmd in def_data['commands']:
                lines.append(f"export interface {cmd['name']} {{")
                for field in cmd['fields']:
                    ts_type = self._get_ts_type(field['type'])
                    unit = f" ({field['unit']})" if 'unit' in field else ""
                    lines.append(f"  {field['name']}: {ts_type}; // {field.get('desc', '')}{unit}")
                lines.append("}\n")
                
        return "\n".join(lines)

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def main():
    parser = argparse.ArgumentParser(description="FT-C600 Protocol Code Generator")
    parser.add_argument('--mode', choices=['qt', 'ts', 'c_sdk', 'all'], default='all')
    parser.add_argument('--uvc_map', default='transports/uvc_xu/mapping.json')
    parser.add_argument('--rtsp_map', default='transports/rtsp_onvif/mapping.json')
    args = parser.parse_args()

    # 初始化路徑
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    gen = ProtocolGenerator(base_dir)

    uvc_map_path = os.path.join(base_dir, args.uvc_map)
    rtsp_map_path = os.path.join(base_dir, args.rtsp_map)

    # 執行產出邏輯
    if args.mode in ['qt', 'all']:
        ensure_dir(os.path.join(base_dir, "dist/cpp_qt"))
        
        # Qt 需要處理 UVC 與 RTSP 兩種連線方式
        if os.path.exists(uvc_map_path):
            uvc_code = gen.generate_uvc_cpp(uvc_map_path)
            with open(os.path.join(base_dir, "dist/cpp_qt/fup_uvc_structs.h"), 'w', encoding='utf-8') as f:
                f.write(uvc_code)
            print("Generated: dist/cpp_qt/fup_uvc_structs.h")
            
        if os.path.exists(rtsp_map_path):
            rtsp_code = gen.generate_rtsp_qt(rtsp_map_path)
            with open(os.path.join(base_dir, "dist/cpp_qt/fup_network_models.h"), 'w', encoding='utf-8') as f:
                f.write(rtsp_code)
            print("Generated: dist/cpp_qt/fup_network_models.h")

    if args.mode in ['c_sdk', 'all']:
        ensure_dir(os.path.join(base_dir, "dist/c"))
        if os.path.exists(uvc_map_path):
            uvc_code = gen.generate_uvc_cpp(uvc_map_path) # C SDK 也共用這套二進位結構
            with open(os.path.join(base_dir, "dist/c/fup_structs.h"), 'w', encoding='utf-8') as f:
                f.write(uvc_code)
            print("Generated: dist/c/fup_structs.h")

    if args.mode in ['ts', 'all']:
        ensure_dir(os.path.join(base_dir, "dist/ts"))
        ts_code = gen.generate_ts()
        with open(os.path.join(base_dir, "dist/ts/protocol.ts"), 'w', encoding='utf-8') as f:
            f.write(ts_code)
        print("Generated: dist/ts/protocol.ts")

if __name__ == "__main__":
    main()