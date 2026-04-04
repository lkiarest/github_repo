#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::{Manager};
use tauri::menu::{MenuBuilder, MenuItemBuilder};
use tauri::tray::{TrayIconBuilder, TrayIconEvent};

fn main() {
    tauri::Builder::default()
        .setup(|app| {
            let show = MenuItemBuilder::with_id("show", "打开窗口").build(app)?;
            let quit = MenuItemBuilder::with_id("quit", "退出").build(app)?;
            let menu = MenuBuilder::new(app).items(&[&show, &quit]).build()?;

            TrayIconBuilder::new()
                .menu(&menu)
                .on_menu_event(|app, event| match event.id().as_ref() {
                    "show" => {
                        let window = app.get_webview_window("main").unwrap();
                        window.show().unwrap();
                        window.set_focus().unwrap();
                    }
                    "quit" => std::process::exit(0),
                    _ => {}
                })
                .build(app)?;

            // 启动后端
            let project_dir = std::env::current_dir().unwrap();
            let script = project_dir.join("launch_control_api_v2.sh");
            std::process::Command::new("bash")
                .arg(script)
                .spawn()
                .expect("failed to start backend");

            let window = app.get_webview_window("main").unwrap();
            window.hide().unwrap();

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error running tauri app");
}
