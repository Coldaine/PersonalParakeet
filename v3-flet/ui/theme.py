#!/usr/bin/env python3
"""
Material Design theme configuration for PersonalParakeet v3
Provides consistent styling across all UI components
"""

import flet as ft


def get_dictation_theme() -> dict:
    """
    Get the dictation view theme configuration
    Provides glass morphism and modern dark theme styling
    """
    return {
        # Glass morphism colors
        'glass_bg': ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
        'glass_border': ft.Colors.with_opacity(0.3, ft.Colors.WHITE),
        'glass_blur': (10, 10),
        
        # Text colors
        'primary_text': ft.Colors.WHITE,
        'secondary_text': ft.Colors.GREY_400,
        'accent_text': ft.Colors.BLUE_300,
        'error_text': ft.Colors.RED_400,
        'success_text': ft.Colors.GREEN_400,
        'warning_text': ft.Colors.AMBER_400,
        
        # Status colors
        'connected_color': ft.Colors.GREEN_500,
        'disconnected_color': ft.Colors.RED_500,
        'listening_color': ft.Colors.BLUE_500,
        'idle_color': ft.Colors.GREY_500,
        
        # Control colors
        'clarity_enabled': ft.Colors.AMBER_500,
        'clarity_disabled': ft.Colors.GREY_500,
        'command_enabled': ft.Colors.PURPLE_500,
        'command_disabled': ft.Colors.GREY_500,
        'commit_button': ft.Colors.GREEN_500,
        'clear_button': ft.Colors.RED_500,
        
        # Confidence colors
        'high_confidence': ft.Colors.GREEN_500,    # > 90%
        'medium_confidence': ft.Colors.ORANGE_500, # 70-90%
        'low_confidence': ft.Colors.RED_500,       # < 70%
        
        # Animation durations
        'fast_transition': 150,    # ms
        'normal_transition': 300,  # ms
        'slow_transition': 500,    # ms
        
        # Sizes
        'border_radius': 15,
        'small_border_radius': 8,
        'padding_small': 10,
        'padding_normal': 15,
        'padding_large': 20,
        'icon_size_small': 16,
        'icon_size_normal': 20,
        'icon_size_large': 24,
        
        # Typography
        'font_size_small': 10,
        'font_size_normal': 14,
        'font_size_large': 18,
        'font_size_xlarge': 24,
        'font_weight_normal': ft.FontWeight.W_400,
        'font_weight_medium': ft.FontWeight.W_500,
        'font_weight_bold': ft.FontWeight.W_700,
    }


def apply_glass_morphism(container: ft.Container, theme: dict = None) -> ft.Container:
    """Apply glass morphism effect to a container"""
    if theme is None:
        theme = get_dictation_theme()
    
    container.bgcolor = theme['glass_bg']
    container.border = ft.border.all(1, theme['glass_border'])
    container.border_radius = theme['border_radius']
    container.blur = ft.Blur(
        theme['glass_blur'][0], 
        theme['glass_blur'][1], 
        ft.BlurTileMode.MIRROR
    )
    
    return container


def create_status_dot(is_active: bool, color_active: str, color_inactive: str, 
                     size: int = 8) -> ft.Container:
    """Create an animated status dot"""
    return ft.Container(
        width=size,
        height=size,
        bgcolor=color_active if is_active else color_inactive,
        border_radius=size // 2,
        animate=ft.Animation(
            duration=1000,
            curve=ft.AnimationCurve.EASE_IN_OUT
        ) if is_active else None
    )


def create_pulse_animation() -> ft.Animation:
    """Create pulse animation for active states"""
    return ft.Animation(
        duration=1500,
        curve=ft.AnimationCurve.EASE_IN_OUT
    )


def create_fade_animation(fast: bool = False) -> ft.Animation:
    """Create fade in/out animation"""
    duration = 150 if fast else 300
    return ft.Animation(
        duration=duration,
        curve=ft.AnimationCurve.EASE_OUT
    )


def get_confidence_color(confidence: float) -> str:
    """Get color based on confidence level"""
    theme = get_dictation_theme()
    
    if confidence > 0.9:
        return theme['high_confidence']
    elif confidence > 0.7:
        return theme['medium_confidence']
    else:
        return theme['low_confidence']


def get_vad_color(is_speaking: bool, is_active: bool = True) -> str:
    """Get color for VAD indicators"""
    theme = get_dictation_theme()
    
    if not is_active:
        return theme['idle_color']
    
    return theme['listening_color'] if is_speaking else theme['idle_color']


class ThemeColors:
    """Extended color palette for PersonalParakeet v3"""
    
    # Glass morphism
    GLASS_BG = ft.Colors.with_opacity(0.1, ft.Colors.BLACK)
    GLASS_BORDER = ft.Colors.with_opacity(0.3, ft.Colors.WHITE)
    GLASS_OVERLAY = ft.Colors.with_opacity(0.05, ft.Colors.WHITE)
    
    # State colors
    ACTIVE = ft.Colors.BLUE_500
    INACTIVE = ft.Colors.GREY_500
    SUCCESS = ft.Colors.GREEN_500
    WARNING = ft.Colors.AMBER_500
    ERROR = ft.Colors.RED_500
    INFO = ft.Colors.BLUE_400
    
    # Text colors
    PRIMARY = ft.Colors.WHITE
    SECONDARY = ft.Colors.GREY_400
    MUTED = ft.Colors.GREY_600
    ACCENT = ft.Colors.BLUE_300
    
    # Feature colors
    CLARITY = ft.Colors.AMBER_500
    COMMAND = ft.Colors.PURPLE_500
    VAD = ft.Colors.CYAN_500
    TRANSCRIPTION = ft.Colors.WHITE


class Animations:
    """Animation presets for PersonalParakeet v3"""
    
    @staticmethod
    def fade_in(duration: int = 300) -> ft.Animation:
        return ft.Animation(
            duration=duration,
            curve=ft.AnimationCurve.EASE_OUT
        )
    
    @staticmethod
    def fade_out(duration: int = 300) -> ft.Animation:
        return ft.Animation(
            duration=duration,
            curve=ft.AnimationCurve.EASE_IN
        )
    
    @staticmethod
    def pulse(duration: int = 1500) -> ft.Animation:
        return ft.Animation(
            duration=duration,
            curve=ft.AnimationCurve.EASE_IN_OUT
        )
    
    @staticmethod
    def slide_up(duration: int = 400) -> ft.Animation:
        return ft.Animation(
            duration=duration,
            curve=ft.AnimationCurve.EASE_OUT
        )


class Typography:
    """Typography scale for PersonalParakeet v3"""
    
    SMALL = 10
    NORMAL = 14
    LARGE = 18
    XLARGE = 24
    XXLARGE = 32
    
    WEIGHT_LIGHT = ft.FontWeight.W_300
    WEIGHT_NORMAL = ft.FontWeight.W_400
    WEIGHT_MEDIUM = ft.FontWeight.W_500
    WEIGHT_BOLD = ft.FontWeight.W_700