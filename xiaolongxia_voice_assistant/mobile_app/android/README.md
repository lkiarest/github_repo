# Android App 打包（最简单方案）

## 方案：WebView 封装（推荐）

### 1. 使用 Android Studio
创建一个 Empty Activity 项目

### 2. 替换 MainActivity
```java
WebView webView = new WebView(this);
setContentView(webView);
webView.getSettings().setJavaScriptEnabled(true);
webView.loadUrl("http://你的服务器IP:8000/mobile_demo/index.html");
```

### 3. 权限
```xml
<uses-permission android:name="android.permission.RECORD_AUDIO" />
<uses-permission android:name="android.permission.INTERNET" />
```

### 4. 打包 APK
Build → Generate APK

---

## 进阶方案
- 使用 Tauri Mobile
- 使用 Flutter

当前推荐先 WebView 快速验证
