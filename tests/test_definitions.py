#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import json
import os

class TestProtocolDefinitions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """在所有測試開始前，載入專案下所有的 JSON 定義與映射表"""
        # 定位專案根目錄 (tests/ 的上一層)
        cls.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.defs_dir = os.path.join(cls.base_dir, 'definitions')
        cls.uvc_map_path = os.path.join(cls.base_dir, 'transports', 'uvc_xu', 'mapping.json')
        cls.rtsp_map_path = os.path.join(cls.base_dir, 'transports', 'rtsp_onvif', 'mapping.json')
        
        # 載入所有 definition JSON
        cls.definitions = {}
        for filename in os.listdir(cls.defs_dir):
            if filename.endswith('.json'):
                with open(os.path.join(cls.defs_dir, filename), 'r', encoding='utf-8') as f:
                    cls.definitions[filename] = json.load(f)

    def _get_type_size(self, field_type, size=1):
        """輔助函數：計算特定型別佔用的 Byte 數"""
        size_map = {
            "uint8": 1, "int8": 1,
            "uint16": 2, "int16": 2,
            "uint32": 4, "int32": 4
        }
        if field_type in ["string", "char"]:
            return size
        return size_map.get(field_type, 1)

    def test_definition_structures(self):
        """測試 1: 確保 JSON 結構完整且欄位 Offset 沒有重疊"""
        for filename, data in self.definitions.items():
            self.assertIn('commands', data, f"檔案 {filename} 缺少 'commands' 欄位")
            
            for cmd in data['commands']:
                self.assertIn('name', cmd, f"{filename} 中的指令缺少 'name'")
                self.assertIn('fields', cmd, f"{filename} - {cmd['name']} 缺少 'fields'")
                
                current_max_offset = -1
                for field in cmd['fields']:
                    self.assertIn('name', field)
                    self.assertIn('type', field)
                    self.assertIn('offset', field)
                    
                    field_size = self._get_type_size(field['type'], field.get('size', 1))
                    
                    # 檢查記憶體是否重疊 (允許間隙 Padding，但不允許衝突)
                    self.assertTrue(
                        field['offset'] >= current_max_offset, 
                        f"💥 嚴重錯誤: {filename} - {cmd['name']} 欄位 '{field['name']}' 發生 offset 重疊！"
                    )
                    current_max_offset = field['offset'] + field_size

    def test_uvc_xu_mapping(self):
        """測試 2: UVC XU 映射表防呆 (ID 衝突與 60-byte 限制)"""
        if not os.path.exists(self.uvc_map_path):
            self.skipTest("UVC mapping.json 不存在，跳過測試")
            
        with open(self.uvc_map_path, 'r', encoding='utf-8') as f:
            mapping = json.load(f)
            
        max_payload = mapping.get('max_payload_size', 60)
        seen_ids = set()
        
        for cmd in mapping['commands']:
            # 檢查 1: Command ID 是否重複 (避免硬體指令衝突)
            cmd_id = cmd['id']
            self.assertNotIn(cmd_id, seen_ids, f"💥 指令 ID 衝突: {cmd_id} 在 UVC Mapping 中被重複使用！")
            seen_ids.add(cmd_id)
            
            # 檢查 2: 定義檔與指令名稱是否存在
            def_file = cmd['definition']
            self.assertIn(def_file, self.definitions, f"找不到指定的定義檔: {def_file}")
            
            def_data = self.definitions[def_file]
            cmd_def = next((c for c in def_data['commands'] if c['name'] == cmd['name']), None)
            self.assertIsNotNone(cmd_def, f"在 {def_file} 內找不到指令 '{cmd['name']}'")
            
            # 檢查 3: 總長度是否超出硬體限制 (最重要的一道防線)
            if cmd_def['fields']:
                last_field = cmd_def['fields'][-1]
                field_size = self._get_type_size(last_field['type'], last_field.get('size', 1))
                total_size = last_field['offset'] + field_size
                self.assertLessEqual(
                    total_size, max_payload, 
                    f"💥 硬體限制超載: 指令 '{cmd['name']}' 總長度 {total_size} bytes，超過 UVC XU {max_payload} bytes 的限制！"
                )

    def test_rtsp_onvif_mapping(self):
        """測試 3: RTSP/ONVIF 網路端點衝突檢查"""
        if not os.path.exists(self.rtsp_map_path):
            self.skipTest("RTSP mapping.json 不存在，跳過測試")
            
        with open(self.rtsp_map_path, 'r', encoding='utf-8') as f:
            mapping = json.load(f)
            
        seen_endpoints = set()
        for cmd in mapping['commands']:
            # 允許相同 endpoint 但不同 HTTP Method (例如 GET /api/ae 和 PATCH /api/ae)
            method_endpoint = f"{cmd['method']} {cmd['endpoint']}"
            self.assertNotIn(
                method_endpoint, seen_endpoints, 
                f"💥 網路 API 衝突: {method_endpoint} 被重複定義！"
            )
            seen_endpoints.add(method_endpoint)

if __name__ == '__main__':
    # 執行測試並顯示詳細輸出
    unittest.main(verbosity=2)