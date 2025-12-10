#!/usr/bin/env python3
"""
Ekombi Motion Capture Parser & QTC Computer
Extracts joint positions from Captury Live CSV and computes QTC sequences.
"""

import csv
import json
import math
from collections import defaultdict

# Column indices (0-indexed) for joint positions in Captury Live CSV
# Each position has X, Y, Z values
JOINT_COLUMNS = {
    'pelvis': (3, 4, 5),           # CenterOfGravity
    'l_hand': (6, 7, 8),           # LWristPositions
    'l_elbow': (12, 13, 14),       # LElbowPositions
    'l_shoulder': (18, 19, 20),    # LShoulderPositions
    'r_hand': (24, 25, 26),        # RWristPositions
    'r_elbow': (30, 31, 32),       # RElbowPositions
    'r_shoulder': (36, 37, 38),    # RShoulderPositions
    'l_foot': (48, 49, 50),        # LAnklePositions
    'l_knee': (54, 55, 56),        # LKneePositions
    'l_hip': (60, 61, 62),         # LHipPositions
    'r_foot': (72, 73, 74),        # RAnklePositions
    'r_knee': (78, 79, 80),        # RKneePositions
    'r_hip': (84, 85, 86),         # RHipPositions
    'spine_base': (132, 133, 134), # SpinePosition
    'spine_mid': (144, 145, 146),  # Spine2Position
    'sternum': (150, 151, 152),    # Spine3Position (chest level)
    'neck': (162, 163, 164),       # NeckPosition
    'head': (168, 169, 170),       # HeadPosition
}

# Joints to use in the QTC viewer
TARGET_JOINTS = [
    'head', 'sternum', 'pelvis', 'l_hand', 'r_hand',
    'l_elbow', 'r_elbow', 'l_foot', 'r_foot', 'spine_mid'
]

# Joint pairs for QTC analysis
QTC_PAIRS = [
    ('l_hand', 'head', 'L Hand ↔ Head'),
    ('r_hand', 'head', 'R Hand ↔ Head'),
    ('l_hand', 'r_hand', 'L Hand ↔ R Hand'),
    ('l_hand', 'pelvis', 'L Hand ↔ Pelvis'),
    ('r_hand', 'pelvis', 'R Hand ↔ Pelvis'),
    ('l_foot', 'pelvis', 'L Foot ↔ Pelvis'),
    ('r_foot', 'pelvis', 'R Foot ↔ Pelvis'),
    ('head', 'pelvis', 'Head ↔ Pelvis'),
]

def distance_3d(p1, p2):
    """Calculate Euclidean distance between two 3D points."""
    return math.sqrt(
        (p1['x'] - p2['x'])**2 +
        (p1['y'] - p2['y'])**2 +
        (p1['z'] - p2['z'])**2
    )

def parse_csv(filepath):
    """Parse Captury Live CSV and extract joint positions."""
    frames = []
    fps = 60.0
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        
        # Skip header rows (first 5 lines)
        for _ in range(5):
            row = next(reader)
            # Extract FPS from second row
            if 'Frame Rate' in str(row):
                try:
                    fps_idx = row.index('Frame Rate')
                    fps = float(row[fps_idx + 1])
                except:
                    pass
        
        # Parse data rows
        for row in reader:
            if len(row) < 170:
                continue
            
            try:
                frame_num = int(row[0])
                frame_data = {'frame': frame_num, 'joints': {}}
                
                for joint_name in TARGET_JOINTS:
                    if joint_name in JOINT_COLUMNS:
                        x_idx, y_idx, z_idx = JOINT_COLUMNS[joint_name]
                        frame_data['joints'][joint_name] = {
                            'x': float(row[x_idx].strip()),
                            'y': float(row[y_idx].strip()),
                            'z': float(row[z_idx].strip())
                        }
                
                frames.append(frame_data)
            except (ValueError, IndexError) as e:
                continue
    
    return frames, fps

def compute_qtc_sequence(frames, joint_a, joint_b, fps, threshold=5.0):
    """
    Compute QTC sequence for a pair of joints.
    
    QTC States:
    - '+0': Approaching (distance decreasing)
    - '0-': Diverging (distance increasing)
    - '00': Stationary (distance stable)
    - '0c': Crossing (direction change detected)
    """
    sequence = []
    prev_delta = None
    
    for i in range(1, len(frames)):
        prev_frame = frames[i - 1]
        curr_frame = frames[i]
        
        t = curr_frame['frame'] / fps
        
        p1_prev = prev_frame['joints'].get(joint_a)
        p2_prev = prev_frame['joints'].get(joint_b)
        p1_curr = curr_frame['joints'].get(joint_a)
        p2_curr = curr_frame['joints'].get(joint_b)
        
        if not all([p1_prev, p2_prev, p1_curr, p2_curr]):
            sequence.append({'t': t, 'state': '00'})
            continue
        
        prev_dist = distance_3d(p1_prev, p2_prev)
        curr_dist = distance_3d(p1_curr, p2_curr)
        delta = curr_dist - prev_dist
        
        # Determine state
        if delta < -threshold:
            state = '+0'  # Approaching
        elif delta > threshold:
            state = '0-'  # Diverging
        else:
            state = '00'  # Stationary
        
        # Detect crossing (direction reversal)
        if prev_delta is not None:
            if (prev_delta < -threshold and delta > threshold) or \
               (prev_delta > threshold and delta < -threshold):
                state = '0c'  # Crossing
        
        prev_delta = delta
        sequence.append({'t': t, 'state': state})
    
    return sequence

def compute_state_distribution(sequence):
    """Calculate distribution of QTC states in a sequence."""
    counts = defaultdict(int)
    for item in sequence:
        counts[item['state']] += 1
    
    total = len(sequence) if sequence else 1
    return {
        'approach': counts['+0'] / total,
        'diverge': counts['0-'] / total,
        'stationary': counts['00'] / total,
        'cross': counts['0c'] / total
    }

def detect_motifs(sequence, pair_id, min_duration=1.0, fps=60):
    """
    Detect recurring motifs in QTC sequence.
    A motif is a distinctive pattern of state changes.
    """
    motifs = []
    
    # Look for approach-then-diverge patterns (characteristic arm gestures)
    i = 0
    motif_count = 0
    while i < len(sequence) - 30:  # Need at least 0.5 seconds
        # Find approach segments
        if sequence[i]['state'] == '+0':
            start_t = sequence[i]['t']
            j = i + 1
            
            # Continue while approaching
            while j < len(sequence) and sequence[j]['state'] in ['+0', '00']:
                j += 1
            
            # Check if followed by diverge
            if j < len(sequence) and sequence[j]['state'] in ['0-', '0c']:
                end_idx = j
                while end_idx < len(sequence) and sequence[end_idx]['state'] in ['0-', '00']:
                    end_idx += 1
                
                end_t = sequence[min(end_idx, len(sequence)-1)]['t']
                duration = end_t - start_t
                
                if duration >= min_duration:
                    motif_count += 1
                    motifs.append({
                        'motif_id': f'{pair_id}_motif_{motif_count}',
                        'pair_id': pair_id,
                        'start_t': round(start_t, 2),
                        'end_t': round(end_t, 2),
                        'label': f'Gesture Pattern {motif_count}',
                        'pattern': 'approach-diverge'
                    })
                
                i = end_idx
            else:
                i = j
        else:
            i += 1
    
    return motifs[:10]  # Limit to 10 most prominent motifs

def normalize_positions(frames):
    """
    Normalize positions to be centered and scaled appropriately for visualization.
    """
    if not frames:
        return frames
    
    # Find bounding box
    min_x = min_y = min_z = float('inf')
    max_x = max_y = max_z = float('-inf')
    
    for frame in frames:
        for joint, pos in frame['joints'].items():
            min_x = min(min_x, pos['x'])
            max_x = max(max_x, pos['x'])
            min_y = min(min_y, pos['y'])
            max_y = max(max_y, pos['y'])
            min_z = min(min_z, pos['z'])
            max_z = max(max_z, pos['z'])
    
    # Center and scale
    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2
    center_z = (min_z + max_z) / 2
    
    scale = max(max_x - min_x, max_y - min_y, max_z - min_z)
    scale = scale if scale > 0 else 1
    
    for frame in frames:
        for joint in frame['joints']:
            frame['joints'][joint]['x'] = (frame['joints'][joint]['x'] - center_x) / scale
            frame['joints'][joint]['y'] = (frame['joints'][joint]['y'] - center_y) / scale
            frame['joints'][joint]['z'] = (frame['joints'][joint]['z'] - center_z) / scale
    
    return frames

def main():
    input_file = '/mnt/user-data/uploads/Sinclair_Ekombi_csv_1.csv'
    output_file = '/home/claude/ekombi-production/ekombi_full_data.json'
    
    print("Parsing Ekombi CSV...")
    frames, fps = parse_csv(input_file)
    print(f"Parsed {len(frames)} frames at {fps} fps")
    
    duration = len(frames) / fps
    print(f"Duration: {duration:.2f} seconds ({duration/60:.1f} minutes)")
    
    # Compute QTC sequences BEFORE normalization (using raw mm values)
    # Threshold of 2.5mm captures meaningful movement while filtering noise
    print("Computing QTC sequences (on raw data)...")
    QTC_THRESHOLD = 2.5  # mm
    qtc_data = {}
    all_motifs = []
    
    for joint_a, joint_b, label in QTC_PAIRS:
        pair_id = f"{joint_a}-{joint_b}"
        print(f"  Processing {pair_id}...")
        
        sequence = compute_qtc_sequence(frames, joint_a, joint_b, fps, threshold=QTC_THRESHOLD)
        distribution = compute_state_distribution(sequence)
        motifs = detect_motifs(sequence, pair_id, min_duration=1.0, fps=fps)
        
        qtc_data[pair_id] = {
            'pair_id': pair_id,
            'joint_a': joint_a,
            'joint_b': joint_b,
            'label': label,
            'sequence': sequence,
            'distribution': distribution
        }
        
        all_motifs.extend(motifs)
        
        print(f"    States: approach={distribution['approach']:.1%}, "
              f"diverge={distribution['diverge']:.1%}, "
              f"stationary={distribution['stationary']:.1%}, "
              f"cross={distribution['cross']:.1%}")
        print(f"    Motifs found: {len(motifs)}")
    
    # NOW normalize positions for visualization (after QTC is computed)
    print("Normalizing positions for visualization...")
    frames = normalize_positions(frames)
    
    # Sort motifs by start time
    all_motifs.sort(key=lambda m: m['start_t'])
    
    # Assign better labels to motifs based on pair and timing
    label_templates = {
        'l_hand-head': ['Reaching Gesture', 'Arm Rise', 'Head Approach', 'Upward Flow'],
        'r_hand-head': ['Mirror Reach', 'Right Arm Rise', 'Counter Gesture', 'Balanced Flow'],
        'l_hand-r_hand': ['Bilateral Wave', 'Arm Coordination', 'Crossing Arms', 'Symmetric Motion'],
        'l_hand-pelvis': ['Cascading Arm', 'Downward Flow', 'Grounding Gesture', 'Center Return'],
        'r_hand-pelvis': ['Right Cascade', 'Settling Motion', 'Balance Point', 'Anchor Movement'],
        'l_foot-pelvis': ['Weight Shift', 'Grounded Step', 'Base Movement', 'Floor Connection'],
        'r_foot-pelvis': ['Counter Step', 'Right Anchor', 'Stability Point', 'Support Shift'],
        'head-pelvis': ['Torso Wave', 'Spinal Flow', 'Core Undulation', 'Vertical Pulse']
    }
    
    pair_counters = defaultdict(int)
    for motif in all_motifs:
        pair_id = motif['pair_id']
        pair_counters[pair_id] += 1
        templates = label_templates.get(pair_id, ['Movement Pattern'])
        idx = (pair_counters[pair_id] - 1) % len(templates)
        motif['label'] = templates[idx]
    
    # Sample frames for output (every 2nd frame to reduce file size)
    sampled_frames = frames[::2]
    
    # Build output data structure
    output_data = {
        'dance_id': 'sinclair_ekombi',
        'title': 'Ekombi',
        'performer': 'Sinclair',
        'tradition': 'Efik/Ibibio',
        'region': 'Cross River, Nigeria',
        'description': 'Efik/Ibibio maiden dance from Cross River, characterized by graceful arm movements that flow like water.',
        'duration': duration,
        'fps': fps,
        'total_frames': len(frames),
        'sampled_frames': len(sampled_frames),
        'sample_rate': 2,
        'joints': TARGET_JOINTS,
        'joint_display_names': {
            'head': 'Head',
            'sternum': 'Sternum', 
            'pelvis': 'Pelvis',
            'l_hand': 'Left Hand',
            'r_hand': 'Right Hand',
            'l_elbow': 'Left Elbow',
            'r_elbow': 'Right Elbow',
            'l_foot': 'Left Foot',
            'r_foot': 'Right Foot',
            'spine_mid': 'Spine Mid'
        },
        'qtc_pairs': [
            {
                'pair_id': f"{a}-{b}",
                'joint_a': a,
                'joint_b': b,
                'label': label,
                'distribution': qtc_data[f"{a}-{b}"]['distribution']
            }
            for a, b, label in QTC_PAIRS
        ],
        'qtc_sequences': {
            pair_id: data['sequence'][::2]  # Sample every 2nd state
            for pair_id, data in qtc_data.items()
        },
        'sam_motifs': all_motifs[:15],  # Top 15 motifs
        'frames': sampled_frames,
        'metadata': {
            'capture_date': '2024-10-17',
            'capture_system': 'Captury Live 1.0.263f',
            'source_file': 'Sinclair_Ekombi_csv_1.csv',
            'qtc_threshold': QTC_THRESHOLD,
            'qtc_variant': 'QTC_B'
        }
    }
    
    # Write output
    print(f"\nWriting output to {output_file}...")
    import os
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f)
    
    # Calculate file size
    file_size = os.path.getsize(output_file) / (1024 * 1024)
    print(f"Output file size: {file_size:.2f} MB")
    
    print("\nDone!")
    print(f"Total motifs identified: {len(all_motifs)}")
    
    return output_data

if __name__ == '__main__':
    main()
