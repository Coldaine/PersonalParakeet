use pyo3::prelude::*;
use crossbeam_channel::{unbounded, Receiver, Sender};
use std::sync::{Arc, Mutex};
use std::collections::HashMap;

mod gui;
mod events;

use gui::GuiApp;
use events::GuiEvent;

#[pyclass(frozen)]
pub struct GuiController {
    event_sender: Sender<GuiEvent>,
    event_receiver: Arc<Mutex<Option<Receiver<GuiEvent>>>>,
    callback_registry: Arc<Mutex<HashMap<String, Py<PyAny>>>>,
}

#[pymethods]
impl GuiController {
    #[new]
    fn new() -> Self {
        let (tx, rx) = unbounded();
        let callbacks = Arc::new(Mutex::new(HashMap::new()));
        let receiver = Arc::new(Mutex::new(Some(rx)));
        
        Self {
            event_sender: tx,
            event_receiver: receiver,
            callback_registry: callbacks,
        }
    }
    
    pub fn run(&self) -> PyResult<()> {
        let receiver = self.event_receiver.lock().unwrap().take()
            .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("GUI already running"))?;
        
        let callbacks_clone = self.callback_registry.clone();
        
        run_gui_thread(receiver, callbacks_clone);
        Ok(())
    }
    
    pub fn register_callback(&self, name: String, callback: Py<PyAny>) -> PyResult<()> {
        self.callback_registry.lock().unwrap().insert(name, callback);
        Ok(())
    }
    
    pub fn update_status(&self, status: String, color: String) -> PyResult<()> {
        let event = GuiEvent::UpdateStatus(status, color);
        self.event_sender.send(event)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
    }
    
    pub fn update_text(&self, text: String, decision: String) -> PyResult<()> {
        let event = GuiEvent::UpdateText(text, decision);
        self.event_sender.send(event)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
    }
    
    pub fn set_recording(&self, is_recording: bool) -> PyResult<()> {
        let event = GuiEvent::SetRecording(is_recording);
        self.event_sender.send(event)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
    }
    
    pub fn show_error(&self, error_message: String) -> PyResult<()> {
        let event = GuiEvent::ShowError(error_message);
        self.event_sender.send(event)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
    }
    
    pub fn set_window_properties(&self, transparent: bool, always_on_top: bool) -> PyResult<()> {
        let event = GuiEvent::SetWindowProperties { transparent, always_on_top };
        self.event_sender.send(event)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
    }
}

fn run_gui_thread(
    receiver: Receiver<GuiEvent>,
    callbacks: Arc<Mutex<HashMap<String, Py<PyAny>>>>
) {
    let options = eframe::NativeOptions {
        viewport: egui::ViewportBuilder::default()
            .with_title("PersonalParakeet v3")
            .with_inner_size([900.0, 800.0])
            .with_transparent(true)
            .with_always_on_top()
            .with_resizable(true),
        ..Default::default()
    };
    
    eframe::run_native(
        "PersonalParakeet v3",
        options,
        Box::new(move |cc| Ok(Box::new(GuiApp::new(cc, receiver, callbacks)))),
    ).unwrap();
}

#[pymodule]
fn personalparakeet_ui(m: &pyo3::Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<GuiController>()?;
    Ok(())
}
