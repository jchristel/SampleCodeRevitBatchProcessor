# Propagate Grids

## Overview
Propagates grid visibility settings from the active view to multiple selected target views. This tool ensures consistent grid display across different views in the project.

## Prerequisites
- Grids present in the current Revit model
- Active view with configured grid visibility
- Target views where grid visibility should be applied

## Functionality
This tool enables:
- Transfer of grid visibility from active view to target views
- Multi-view selection for batch operations
- Support for different plan view types
- Consistent grid display management across views

## Usage Steps
1. Set up grid visibility in the current active view as desired
2. Click the "Propagate Grids" button
3. Select target views from the multi-select interface
4. Confirm the propagation operation
5. Review results and any status messages

## Supported View Types
The tool works with:
- **Floor Plans**: Standard architectural floor plans
- **Ceiling Plans**: Reflected ceiling plans (RCP)
- **Area Plans**: Area calculation and planning views

## View Selection Interface
- Displays views with type identification
- Format: "View Name (View Type)"
- Multi-select capability for batch processing
- Sorted alphabetically for easy navigation

## Grid Propagation Process
- Copies grid visibility settings from active view
- Applies settings to all selected target views
- Maintains grid appearance consistency
- Preserves other view-specific settings

## Input Requirements
- Active view with grid elements
- Target views of supported types
- Grids must be available in the model
- Write permissions for view modifications

## Output
- Updated grid visibility in target views
- Status messages for successful propagation
- Error reporting for any failed operations
- Consistent grid display across selected views

## Operation Details
- Preserves existing view settings unrelated to grids
- Only affects grid visibility and display
- Maintains view-specific scale and other properties
- Works with both model grids and reference grids

## Error Handling
- Validates view compatibility
- Handles views without grid access
- Provides clear error messages
- Continues processing remaining views after failures

## Performance Considerations
- Efficient batch processing
- Minimal impact on model performance
- Quick execution for multiple views
- Memory-efficient operation

## Best Practices
- Configure source view grid visibility carefully
- Review target view selection before propagation
- Test on a few views before large batch operations
- Consider view template usage for consistency
- Document grid visibility standards for the project