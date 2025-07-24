# Workshop Box Adaptive Sizing Specification

## Overview
The Workshop Box must intelligently adapt its size and position based on content length, screen resolution, and user context. This document specifies the three-state breathing system and transition logic.

## Breathing States

### 1. Compact Mode (1-10 words)
- **Dimensions**: 
  - Width: 400-600px (scaled by DPI)
  - Height: 60-80px (single line)
- **Position**: 20px offset from cursor
- **Appearance**: Tooltip-like, minimal shadow
- **Use Case**: Quick corrections, short phrases

### 2. Standard Mode (10-50 words)
- **Dimensions**:
  - Width: 600-900px (scaled by DPI)
  - Height: 80-200px (2-4 lines)
- **Position**: 30-50px offset from cursor, shifts to avoid edges
- **Appearance**: Subtle drop shadow, slightly more prominent
- **Use Case**: Normal dictation sentences

### 3. Extended Mode (50+ words)
- **Dimensions**:
  - Width: 900-1200px (scaled by DPI, max 30% screen width)
  - Height: 200-400px (5-10 lines with scroll)
- **Position**: Docks to nearest screen edge
- **Appearance**: Stronger shadow, scroll indicators
- **Use Case**: Long-form dictation, paragraphs

## DPI Scaling Formula

```python
def calculate_scale_factor(screen_info):
    # Base scaling
    dpi_scale = screen_info.dpi / 96.0  # 96 DPI is standard
    
    # Resolution-based scaling
    resolution_scale = min(screen_info.width / 1920.0, 2.0)
    
    # Combined scale (prefer larger of the two)
    final_scale = max(dpi_scale, resolution_scale)
    
    # Apply to all dimensions
    return {
        'scale': final_scale,
        'base_font_size': 14 * final_scale,
        'padding': 20 * final_scale,
        'corner_radius': 8 * final_scale
    }
```

## Transition Timing

### Size Transitions
- **Growth**: 150ms ease-out curve
- **Shrink**: 200ms ease-in-out curve
- **Mode Change**: 250ms with subtle bounce effect

### Position Transitions
- **Cursor Following**: 100ms linear (fast, responsive)
- **Edge Docking**: 300ms ease-in-out
- **Collision Avoidance**: 150ms ease-out

## Smart Positioning Algorithm

```python
class AdaptivePositioner:
    def __init__(self, screen_info):
        self.screen = screen_info
        self.edge_margin = 50 * screen_info.scale
        self.cursor_offset = 30 * screen_info.scale
        
    def calculate_position(self, cursor, box_size, current_mode):
        if current_mode == 'compact':
            return self._position_near_cursor(cursor, box_size)
        elif current_mode == 'standard':
            return self._position_with_smart_offset(cursor, box_size)
        else:  # extended
            return self._position_docked(cursor, box_size)
    
    def _position_near_cursor(self, cursor, box_size):
        # Quadrant-based positioning
        quadrant = self._get_cursor_quadrant(cursor)
        
        # Position in opposite quadrant to avoid covering content
        if quadrant == 'top-left':
            x = cursor.x + self.cursor_offset
            y = cursor.y + self.cursor_offset
        elif quadrant == 'top-right':
            x = cursor.x - box_size.width - self.cursor_offset
            y = cursor.y + self.cursor_offset
        # ... etc
        
        return self._ensure_on_screen(x, y, box_size)
```

## Visual Design Constants

```python
WORKSHOP_BOX_STYLES = {
    'compact': {
        'bg_opacity': 0.85,
        'border_opacity': 0.3,
        'shadow_blur': 10,
        'shadow_offset': 2
    },
    'standard': {
        'bg_opacity': 0.88,
        'border_opacity': 0.4,
        'shadow_blur': 15,
        'shadow_offset': 3
    },
    'extended': {
        'bg_opacity': 0.92,
        'border_opacity': 0.5,
        'shadow_blur': 20,
        'shadow_offset': 5
    }
}
```

## Content Layout Rules

### Text Rendering
- Font: System monospace (Consolas on Windows, SF Mono on Mac, Ubuntu Mono on Linux)
- Line Height: 1.4x font size
- Word Wrap: Break at word boundaries, hyphenate long words
- Highlighting: Changed words pulse briefly (300ms)

### Overflow Handling
- Compact Mode: Ellipsis (...) for overflow
- Standard Mode: Fade last line if more content exists
- Extended Mode: Smooth scrolling with momentum

## Animation Curves

```python
# Easing functions for smooth transitions
def ease_out_cubic(t):
    return 1 - pow(1 - t, 3)

def ease_in_out_quad(t):
    return 2 * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 2) / 2

def bounce_out(t):
    n1, d1 = 7.5625, 2.75
    if t < 1 / d1:
        return n1 * t * t
    elif t < 2 / d1:
        t -= 1.5 / d1
        return n1 * t * t + 0.75
    # ... etc
```

## Performance Targets

- **Resize Calculation**: < 1ms
- **Position Update**: < 2ms
- **Render Frame**: < 16ms (60 FPS)
- **Animation Step**: < 5ms

## Edge Cases

1. **Multiple Monitors**: Box should stay on active monitor
2. **Screen Edge**: Flip to opposite side if too close to edge
3. **Cursor at Screen Edge**: Use center screen as fallback
4. **Rapid Mode Changes**: Queue transitions, don't stack
5. **Minimize/Maximize**: Pause rendering when not visible

## Accessibility Considerations

- **High Contrast Mode**: Increase opacity to 0.95+
- **Reduced Motion**: Disable animations, instant transitions
- **Screen Readers**: Announce mode changes
- **Keyboard Navigation**: Tab through scrollable content

## Future Considerations

- **Gesture Support**: Swipe to dismiss/dock
- **Multi-Box Mode**: Show history in secondary boxes
- **Themes**: User-customizable colors and opacity
- **Smart Docking**: Remember preferred positions per app