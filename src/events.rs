#[derive(Debug, Clone)]
pub enum GuiEvent {
    UpdateStatus(String, String),
    UpdateText(String, String),
    SetRecording(bool),
    ShowError(String),
    SetWindowProperties { transparent: bool, always_on_top: bool },
    TriggerCallback(String, String),
}

impl GuiEvent {
    pub fn is_high_frequency(&self) -> bool {
        matches!(self, GuiEvent::UpdateText(_, _) | GuiEvent::UpdateStatus(_, _))
    }
}
