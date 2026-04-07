// 引入由 gen_protocol.py 產出的強型別介面
import { BARCODE_RESULT } from '../../dist/ts/protocol';

/**
 * 模擬 React Component 中的 API 呼叫
 */
async function pollBarcodeResult(): Promise<BARCODE_RESULT | null> {
    console.log("=== OmniSight-Forge TS API Client ===");
    
    // 實際開發中，這裡會是: await fetch('/api/v1/barcode/latest')
    const mockResponse: BARCODE_RESULT = {
        echo: 144,
        queue_count: 0,
        seq_number: 1004,
        status: 1,
        format_id: 1,
        format_name: "QR Code",
        total_len: 17,
        text_preview: "[https://google.com](https://google.com)",
        flags: 0
    };

    return mockResponse;
}

// 測試呼叫
pollBarcodeResult().then(result => {
    if (result && result.status === 1) {
        // TypeScript 會提供自動完成，且若打錯字 (如 result.seq_num) 會在編譯時報錯
        console.log(`[Decoded ID: ${result.seq_number}] [${result.format_name}] ${result.text_preview}`);
    }
});