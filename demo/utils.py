"""Utility functions for the chat UI."""

def calculate_zip_distance(zip1: str, zip2: str) -> float:
    """
    Calculate estimated distance between two zip codes.
    
    Uses simple numeric difference heuristic for demo.
    In production, would call Google Maps Distance API.
    
    Args:
        zip1: First zip code
        zip2: Second zip code
        
    Returns:
        Estimated distance in miles
    """
    try:
        z1 = int(zip1)
        z2 = int(zip2)
        zip_diff = abs(z1 - z2)
        
        # Rough approximation for demo
        if zip_diff == 0:
            return 0.0
        elif zip_diff <= 5:
            return min(zip_diff * 0.5, 3.0)
        elif zip_diff <= 10:
            return min(zip_diff * 1.2, 12.0)
        else:
            return min(zip_diff * 1.5, 15.0)
    except:
        return 10.0


def get_distance_color(distance: float, max_distance: float) -> str:
    """
    Get color for distance display based on whether it exceeds limit.
    
    Args:
        distance: Actual distance in miles
        max_distance: Maximum acceptable distance
        
    Returns:
        Color string (green, orange, or red)
    """
    if distance <= max_distance * 0.5:
        return "green"
    elif distance <= max_distance:
        return "orange"
    else:
        return "red"


def format_distance(distance: float) -> str:
    """Format distance for display."""
    if distance < 0.5:
        return "< 0.5 mi"
    elif distance < 1.0:
        return f"{distance:.1f} mi"
    else:
        return f"{distance:.0f} mi"

