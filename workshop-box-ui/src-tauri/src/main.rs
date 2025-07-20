// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::{Manager, Window};
use tokio_tungstenite::{connect_async, tungstenite::protocol::Message};
use futures_util::{StreamExt, SinkExt};

#[derive(Clone, serde::Serialize)]
struct TranscriptionPayload {
    text: String,
    mode: String,
    confidence: f32,
}

// Learn more about Tauri commands at https://tauri.app/v1/guides/features/command
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[tauri::command]
async fn update_position(window: Window, x: i32, y: i32) {
    window.set_position(tauri::Position::Physical(tauri::PhysicalPosition { x, y })).unwrap();
}

#[tauri::command]
async fn update_size(window: Window, width: u32, height: u32) {
    window.set_size(tauri::Size::Physical(tauri::PhysicalSize { width, height })).unwrap();
}

async fn connect_to_python_backend(app_handle: tauri::AppHandle) {
    loop {
        println!("Attempting to connect to Python backend at ws://localhost:8765");
        
        match connect_async("ws://localhost:8765").await {
            Ok((ws_stream, _)) => {
                println!("Connected to Python backend!");
                let (mut ws_sender, mut ws_receiver) = ws_stream.split();
                
                // Send initial connection message
                let _ = ws_sender.send(Message::Text(r#"{"type":"client_connected","client":"tauri"}"#.to_string())).await;
                
                while let Some(msg) = ws_receiver.next().await {
                    match msg {
                        Ok(Message::Text(text)) => {
                            // Parse message from Python backend
                            if let Ok(data) = serde_json::from_str::<serde_json::Value>(&text) {
                                if data["type"] == "transcription" {
                                    // Emit to frontend
                                    let _ = app_handle.emit_all("transcription", TranscriptionPayload {
                                        text: data["text"].as_str().unwrap_or("").to_string(),
                                        mode: data["mode"].as_str().unwrap_or("standard").to_string(),
                                        confidence: data["confidence"].as_f64().unwrap_or(0.9) as f32,
                                    });
                                }
                            }
                        }
                        Ok(Message::Close(_)) => {
                            println!("Python backend closed connection");
                            break;
                        }
                        Err(e) => {
                            println!("WebSocket error: {:?}", e);
                            break;
                        }
                        _ => {}
                    }
                }
            }
            Err(e) => {
                println!("Failed to connect to Python backend: {:?}", e);
            }
        }
        
        // Wait 3 seconds before reconnecting
        println!("Reconnecting in 3 seconds...");
        tokio::time::sleep(tokio::time::Duration::from_secs(3)).await;
    }
}

fn main() {
    tauri::Builder::default()
        .setup(|app| {
            let handle = app.handle();
            
            // Connect to Python WebSocket server as a client
            tauri::async_runtime::spawn(async move {
                connect_to_python_backend(handle).await;
            });
            
            // Get the main window
            let window = app.get_window("main").unwrap();
            
            // Set window properties for overlay
            #[cfg(target_os = "windows")]
            {
                // Don't make click-through yet - let user interact first
                window.set_ignore_cursor_events(false).unwrap();
                
                // Set window to be always on top
                window.set_always_on_top(true).unwrap();
            }
            
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![greet, update_position, update_size])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}