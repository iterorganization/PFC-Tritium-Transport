import numpy as np
from scipy.spatial import cKDTree

def interpolate_segments(source_segments, source_values, target_segments, resolution_factor=10):
    """
    Maps data from source_segments to target_segments by finding the closest segment.
    
    Parameters:
    - source_segments: List of (x1, y1, x2, y2) defining source line segments
    - source_values: List of values corresponding to each source segment
    - target_segments: List of (x1, y1, x2, y2) defining target line segments
    - resolution_factor: Factor by which segment resolution is increased
    
    Returns:
    - mapped_values: List of values assigned to each target segment
    """
    
    # Function to generate intermediate points along segments
    def densify_segment(x1, y1, x2, y2, factor):
        return np.linspace([x1, y1], [x2, y2], factor, endpoint=True)
    
    # Increase resolution of source segments
    fine_source_points = []
    fine_source_values = []
    
    for (x1, y1, x2, y2), value in zip(source_segments, source_values):
        points = densify_segment(x1, y1, x2, y2, resolution_factor)
        fine_source_points.extend(points)
        fine_source_values.extend([value] * len(points))  # Keep values constant over subsegments
    
    fine_source_points = np.array(fine_source_points)
    fine_source_values = np.array(fine_source_values)
    
    # Increase resolution of target segments
    fine_target_points = []
    target_indices = list(range(len(target_segments)))  # Create index mapping for target segments
    
    for (x1, y1, x2, y2) in target_segments:
        points = densify_segment(x1, y1, x2, y2, resolution_factor)
        fine_target_points.extend(points)
    
    fine_target_points = np.array(fine_target_points)
  
    # Create KD-tree for fast nearest-neighbor search
    tree = cKDTree(fine_source_points)
    
    # Map target segments to closest fine source points
    mapped_values_dict = {idx: [] for idx in target_indices}
    
    for i, point in enumerate(fine_target_points):
        dist, nearest_idx = tree.query(point)  # Find nearest fine source point
        mapped_values_dict[i // resolution_factor].append(fine_source_values[nearest_idx])
    
    # Average mapped values per original target segment index
    mapped_values = [np.mean(mapped_values_dict[idx]) for idx in target_indices]
    
    return mapped_values

# Example Usage
# source_segments = [(0, 0, 1, 1), (1, 1, 2, 2), (2, 2, 3, 3), (3, 3, 4, 4)]
# source_values = [10, 20, 10, 20]
# target_segments = [(0.2, 0.2, 1.2, 1.2), (1.2, 1.2, 2.2, 2.2), (2.2, 2.2, 3.2, 3.2), (3.2, 3.2, 4.2, 4.2)]

# mapped_values = interpolate_segments(source_segments, source_values, target_segments)
# print("Mapped Values:", mapped_values)
