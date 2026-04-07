/*
 * FT-C600 Universal Protocol - Endian Utilities
 * Provides consistent Little-Endian conversion across Windows and Linux.
 */

#ifndef FUP_ENDIAN_UTILS_H
#define FUP_ENDIAN_UTILS_H

#include <stdint.h>

// 偵測是否為 Qt 環境，優先使用 Qt 內建的高效率工具
#ifdef QT_CORE_LIB
    #include <QtEndian>
    #define FUP_FROM_LE16(x) qFromLittleEndian<uint16_t>(x)
    #define FUP_FROM_LE32(x) qFromLittleEndian<uint32_t>(x)
#else
    // 非 Qt 環境 (如純 MFC 或 Embedded SDK)
    #if defined(_MSC_VER)
        // Windows / MSVC 專屬內建函式
        #include <stdlib.h>
        #define FUP_FROM_LE16(x) (x)
        #define FUP_FROM_LE32(x) (x)
        // 若未來需要支援大端序平台，可在此處使用 _byteswap_ushort/ulong
    #elif defined(__GNUC__) || defined(__clang__)
        // Linux / GCC / Clang 專屬內建函式
        #define FUP_FROM_LE16(x) (x)
        #define FUP_FROM_LE32(x) (x)
        // 若為大端序架構，則使用 __builtin_bswap16/32
    #else
        // 通用型實作 (備援)
        static inline uint16_t fup_swap16(uint16_t x) {
            return (uint16_t)((x << 8) | (x >> 8));
        }
        static inline uint32_t fup_swap32(uint32_t x) {
            return (uint32_t)((x << 24) | ((x << 8) & 0xff0000) | 
                             ((x >> 8) & 0xff00) | (x >> 24));
        }
        #define FUP_FROM_LE16(x) (x)
        #define FUP_FROM_LE32(x) (x)
    #endif
#endif

/**
 * @brief 封裝結構體欄位讀取的輔助巨集
 * 確保開發者在讀取如 u32CurrIntt 等 4-byte 欄位時，會強制意識到端序問題 
 */
#define FUP_GET_U16(field) FUP_FROM_LE16(field)
#define FUP_GET_U32(field) FUP_FROM_LE32(field)

#endif // FUP_ENDIAN_UTILS_H