cmake_minimum_required(VERSION 3.16)
project(FTC600Protocol LANGUAGES CXX)

# --------------------------------------------------------------------
# 1. 環境檢查與路徑定義
# --------------------------------------------------------------------
find_package(Python3 REQUIRED COMPONENTS Interpreter)

# 定義各個目錄的絕對路徑，方便跨專案引用
set(PROTOCOL_ROOT_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../..")
set(GENERATOR_SCRIPT  "${PROTOCOL_ROOT_DIR}/generators/gen_protocol.py")
set(DEFINITION_DIR    "${PROTOCOL_ROOT_DIR}/definitions")
set(OUTPUT_DIR_QT     "${PROTOCOL_ROOT_DIR}/dist/cpp_qt")

# 列出所有的 JSON 定義檔，作為依賴項
file(GLOB PROTOCOL_JSONS "${DEFINITION_DIR}/*.json")

# --------------------------------------------------------------------
# 2. 自動化生成指令 (Custom Command)
# --------------------------------------------------------------------
# 這裡定義了：當 JSON 有變動時，CMake 會自動執行 Python 腳本產出 Header
add_custom_command(
    OUTPUT "${OUTPUT_DIR_QT}/protocol_defs.h"
    COMMAND ${Python3_EXECUTABLE} "${GENERATOR_SCRIPT}" --mode qt
    DEPENDS ${PROTOCOL_JSONS} "${GENERATOR_SCRIPT}"
    WORKING_DIRECTORY "${PROTOCOL_ROOT_DIR}"
    COMMENT "FUP: Generating Qt/C++ compatible protocol headers from JSON definitions..."
    VERBATIM
)

# --------------------------------------------------------------------
# 3. 定義 Interface Library (供外部專案連結)
# --------------------------------------------------------------------
# 使用 INTERFACE 類型是因為協議庫主要是標頭檔，不需要編譯成 .lib 或 .so
add_library(ftc600_protocol INTERFACE)

# 確保生成指令被執行
add_custom_target(generate_protocol_headers DEPENDS "${OUTPUT_DIR_QT}/protocol_defs.h")
add_dependencies(ftc600_protocol generate_protocol_headers)

# 設定 Include 路徑，讓外部專案可以直接 #include "cpp_qt/protocol_defs.h"
target_include_directories(ftc600_protocol INTERFACE 
    "${PROTOCOL_ROOT_DIR}/dist"
)

# 針對跨平台 (Windows/Linux) 與架構 (x64/ARM64) 的編譯建議
if(MSVC)
    target_compile_options(ftc600_protocol INTERFACE /W4)
else()
    target_compile_options(ftc600_protocol INTERFACE -Wall -Wextra)
endif()

# --------------------------------------------------------------------
# 4. 安裝與匯出 (選用，方便未來作為套件發佈)
# --------------------------------------------------------------------
message(STATUS "FT-C600 Protocol Library configured for Target: ${CMAKE_SYSTEM_PROCESSOR}")