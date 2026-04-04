#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::process::Command;
use tauri::{Manager, SystemTray, SystemTrayEvent, SystemTrayMenu, CustomMenuItem};

fn main() {
    let show = CustomMenuItem::new("show".to_string(), "打开窗口");
    let quit = CustomMenuItem::new("quit".to_string(), "退出");

    let tray_menu = SystemTrayMenu::new()
        .add_item(show)
        .add_item(quit);

    let tray = SystemTray::new().with_menu(tray_menu);

    tauri::Builder::default()
        .system_tray(tray)
        .setup(|app| {
            // 🚀 启动后端
            let project_dir = std::env::current_dir().unwrap();
            let script = project_dir.join("launch_control_api.sh");

            let _child = Command::new("bash")
                .arg(script)
                .spawn()
                .expect("failed to start backend");

            let window = app.get_window("main").unwrap();
            window.hide().unwrap();

            Ok(())
        })
        .on_system_tray_event(|app, event| match event {
            SystemTrayEvent::MenuItemClick { id, .. } => match id.as_str() {
                "show" => {
                    let window = app.get_window("main").unwrap();
                    window.show().unwrap();
                    window.set_focus().unwrap();
                }
                "quit" => {
                    std::process::exit(0);
                }
                _ => {}
            },
            _ => {}
        })
        .run(tauri::generate_context!())
        .expect("error running tauri app");
}
