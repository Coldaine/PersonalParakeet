use eframe::egui;
use crossbeam_channel::Receiver;
use std::sync::{Arc, Mutex};
use std::collections::HashMap;
use pyo3::prelude::*;
use crate::events::GuiEvent;

pub struct GuiApp {
    receiver: Receiver<GuiEvent>,
    callbacks: Arc<Mutex<HashMap<String, Py<PyAny>>>>,
    
    status_text: String,
    status_color: egui::Color32,
    recognized_text: String,
    text_color: egui::Color32,
    is_recording: bool,
    debug_mode: bool,
    settings_open: bool,
    
    thought_linking_enabled: bool,
    vad_threshold: f32,
    
    last_update: std::time::Instant,
    update_batch: Vec<GuiEvent>,
}

impl GuiApp {
    pub fn new(
        _cc: &eframe::CreationContext<'_>,
        receiver: Receiver<GuiEvent>,
        callbacks: Arc<Mutex<HashMap<String, Py<PyAny>>>>
    ) -> Self {
        Self {
            receiver,
            callbacks,
            status_text: "Ready".to_string(),
            status_color: egui::Color32::WHITE,
            recognized_text: String::new(),
            text_color: egui::Color32::WHITE,
            is_recording: false,
            debug_mode: false,
            settings_open: false,
            thought_linking_enabled: false,
            vad_threshold: 2.0,
            last_update: std::time::Instant::now(),
            update_batch: Vec::new(),
        }
    }
    
    fn process_events(&mut self) {
        self.update_batch.clear();
        while let Ok(event) = self.receiver.try_recv() {
            self.update_batch.push(event);
            if self.update_batch.len() >= 10 {
                break;
            }
        }
        
        for event in &self.update_batch {
            match event {
                GuiEvent::UpdateStatus(status, color) => {
                    self.status_text = status.clone();
                    self.status_color = parse_color(color);
                }
                GuiEvent::UpdateText(text, decision) => {
                    match decision.as_str() {
                        "APPEND_WITH_SPACE" => {
                            if !self.recognized_text.is_empty() {
                                self.recognized_text.push(' ');
                            }
                            self.recognized_text.push_str(text);
                        }
                        "REPLACE" => {
                            self.recognized_text = text.clone();
                        }
                        _ => {
                            self.recognized_text = text.clone();
                        }
                    }
                    self.text_color = egui::Color32::WHITE;
                }
                GuiEvent::SetRecording(recording) => {
                    self.is_recording = *recording;
                    if *recording {
                        self.status_text = "Recording...".to_string();
                        self.status_color = egui::Color32::RED;
                    } else {
                        self.status_text = "Ready".to_string();
                        self.status_color = egui::Color32::GREEN;
                    }
                }
                GuiEvent::ShowError(error) => {
                    self.status_text = format!("Error: {}", error);
                    self.status_color = egui::Color32::from_rgb(255, 165, 0);
                }
                GuiEvent::SetWindowProperties { transparent: _, always_on_top: _ } => {
                }
                GuiEvent::TriggerCallback(callback_name, data) => {
                    self.trigger_python_callback(callback_name, data);
                }
            }
        }
    }
    
    fn trigger_python_callback(&self, callback_name: &str, data: &str) {
        if let Ok(callbacks) = self.callbacks.lock() {
            if let Some(callback) = callbacks.get(callback_name) {
                Python::with_gil(|py| {
                    let args = (data,);
                    if let Err(e) = callback.call1(py, args) {
                        eprintln!("Error calling Python callback {}: {}", callback_name, e);
                    }
                });
            }
        }
    }
}

impl eframe::App for GuiApp {
    fn clear_color(&self, _visuals: &egui::Visuals) -> [f32; 4] {
        [0.0, 0.0, 0.0, 0.0]
    }
    
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        self.process_events();
        
        egui::CentralPanel::default()
            .frame(egui::Frame::none())
            .show(ctx, |ui| {
                ui.horizontal(|ui| {
                    ui.colored_label(self.status_color, &self.status_text);
                    ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                        if ui.button("⚙").clicked() {
                            self.settings_open = true;
                        }
                        if ui.button("🐛").clicked() {
                            self.debug_mode = !self.debug_mode;
                        }
                    });
                });
                
                ui.separator();
                
                egui::ScrollArea::vertical()
                    .auto_shrink([false; 2])
                    .show(ui, |ui| {
                        ui.colored_label(self.text_color, &self.recognized_text);
                    });
                
                if self.debug_mode {
                    ui.separator();
                    ui.collapsing("Debug Info", |ui| {
                        ui.label(format!("Recording: {}", self.is_recording));
                        ui.label(format!("Text length: {}", self.recognized_text.len()));
                        ui.label(format!("Last update: {:?}", self.last_update.elapsed()));
                    });
                }
            });
        
        if self.settings_open {
            egui::Window::new("Settings")
                .open(&mut self.settings_open)
                .show(ctx, |ui| {
                    ui.checkbox(&mut self.thought_linking_enabled, "Enable Thought Linking");
                    ui.add(egui::Slider::new(&mut self.vad_threshold, 0.5..=5.0)
                        .text("VAD Pause Threshold"));
                });
        }
        
        ctx.request_repaint();
    }
}

fn parse_color(color_str: &str) -> egui::Color32 {
    match color_str.to_lowercase().as_str() {
        "red" => egui::Color32::RED,
        "green" => egui::Color32::GREEN,
        "blue" => egui::Color32::BLUE,
        "yellow" => egui::Color32::YELLOW,
        "orange" => egui::Color32::from_rgb(255, 165, 0),
        _ => egui::Color32::WHITE,
    }
}
