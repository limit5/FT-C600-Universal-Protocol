#include <QCoreApplication>
#include <QJsonObject>
#include <QJsonDocument>
#include <QDebug>

// 引入自動生成的雙軌標頭檔
#include "fup_uvc_structs.h"   // 供 USB 使用的二進位結構
#include "fup_network_models.h"// 供 RTSP/CGI 使用的 JSON 模型

// 定義連線模式枚舉
enum class ConnectionType { USB_UVC, NETWORK_RTSP };

class CameraController {
private:
    ConnectionType currentConn;

    // 模擬底層發送 USB UVC 指令
    void sendUvcCommand(uint8_t cmdId, const void* payload, size_t size) {
        qDebug() << "[USB] Sending XU Command:" << hex << cmdId << "Size:" << size;
    }

    // 模擬底層發送 HTTP JSON 請求
    void sendHttpCommand(const QString& endpoint, const QJsonObject& payload) {
        qDebug() << "[Network] Sending POST to:" << endpoint;
        qDebug().noquote() << QJsonDocument(payload).toJson(QJsonDocument::Compact);
    }

public:
    CameraController(ConnectionType type) : currentConn(type) {}

    // 統一的業務邏輯 API：設定目標亮度
    void setTargetLuminance(int luma) {
        if (currentConn == ConnectionType::USB_UVC) {
            // --- 使用 UVC 二進位模式 ---
            AE_STATUS_t aeUvc = {0}; // 初始化為 0
            aeUvc.echo = 0x83;
            aeUvc.target_luma = static_cast<uint8_t>(luma);
            // 透過 60-byte 封包發送
            sendUvcCommand(0x83, &aeUvc, sizeof(AE_STATUS_t));
        } 
        else if (currentConn == ConnectionType::NETWORK_RTSP) {
            // --- 使用 RTSP/CGI 網路模式 ---
            AE_STATUS_Net aeNet;
            aeNet.target_luma = luma;
            // 透過 JSON 發送
            sendHttpCommand("/api/v1/imaging/ae_status", aeNet.toJson());
        }
    }
};

int main(int argc, char *argv[]) {
    QCoreApplication a(argc, argv);

    qDebug() << "=== Qt Dual Transport Demo ===";
    
    CameraController usbCam(ConnectionType::USB_UVC);
    usbCam.setTargetLuminance(140);

    qDebug() << "------------------------------";

    CameraController ipCam(ConnectionType::NETWORK_RTSP);
    ipCam.setTargetLuminance(140);

    return 0;
}