import os
import xml.etree.ElementTree as ET
from pathlib import Path

def convert_pascalvoc_to_yolov8(xml_dir, output_dir, class_list):
    """
    Convert PascalVOC XML annotations to YOLOv8 format
    
    Args:
        xml_dir: Directory containing PascalVOC XML files
        output_dir: Output directory for YOLOv8 labels
        class_list: List of class names in order
    """
    
    # Convert to Path object and check if directory exists
    xml_path = Path(xml_dir)
    print(f"Looking for XML files in: {xml_path.absolute()}")
    
    if not xml_path.exists():
        print(f"ERROR: Directory {xml_path} does not exist!")
        return
    
    if not xml_path.is_dir():
        print(f"ERROR: {xml_path} is not a directory!")
        return
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output directory: {output_dir}")
    
    # Create class mapping
    class_to_id = {class_name: idx for idx, class_name in enumerate(class_list)}
    print(f"Class mapping: {class_to_id}")
    
    # Find XML files
    xml_files = list(xml_path.glob("*.xml"))
    print(f"Found {len(xml_files)} XML files")
    
    if len(xml_files) == 0:
        print("No XML files found! Checking what files are in the directory:")
        all_files = list(xml_path.glob("*"))
        for file in all_files[:10]:  # Show first 10 files
            print(f"  - {file.name}")
        if len(all_files) > 10:
            print(f"  ... and {len(all_files) - 10} more files")
        return
    
    # Process each XML file
    converted_count = 0
    for xml_file in xml_files:
        try:
            print(f"Processing: {xml_file.name}")
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Get image dimensions
            size = root.find("size")
            if size is None:
                print(f"  Warning: No size element in {xml_file.name}")
                continue
                
            width_elem = size.find("width")
            height_elem = size.find("height")
            
            if width_elem is None or height_elem is None:
                print(f"  Warning: Missing width or height in {xml_file.name}")
                continue
                
            width = int(width_elem.text)
            height = int(height_elem.text)
            print(f"  Image dimensions: {width}x{height}")
            
            # Create output text file
            txt_filename = xml_file.stem + ".txt"
            txt_path = os.path.join(output_dir, txt_filename)
            
            objects_found = 0
            with open(txt_path, "w") as f:
                # Find all objects in the XML
                for obj in root.findall("object"):
                    name_elem = obj.find("name")
                    if name_elem is None:
                        continue
                        
                    class_name = name_elem.text.strip()
                    
                    if class_name not in class_to_id:
                        print(f"  Warning: Class '{class_name}' not in class list, skipping...")
                        continue
                    
                    class_id = class_to_id[class_name]
                    
                    # Get bounding box coordinates
                    bbox = obj.find("bndbox")
                    if bbox is None:
                        continue
                    
                    try:
                        xmin = float(bbox.find("xmin").text)
                        ymin = float(bbox.find("ymin").text)
                        xmax = float(bbox.find("xmax").text)
                        ymax = float(bbox.find("ymax").text)
                        
                        # Convert to YOLO format (normalized center coordinates)
                        x_center = (xmin + xmax) / 2 / width
                        y_center = (ymin + ymax) / 2 / height
                        bbox_width = (xmax - xmin) / width
                        bbox_height = (ymax - ymin) / height
                        
                        # Write to file
                        f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {bbox_width:.6f} {bbox_height:.6f}\n")
                        objects_found += 1
                        
                    except (ValueError, AttributeError) as e:
                        print(f"  Error parsing bbox coordinates in {xml_file.name}: {e}")
                        continue
            
            print(f"  Converted: {xml_file.name} -> {objects_found} objects")
            converted_count += 1
            
        except ET.ParseError as e:
            print(f"ERROR: XML parsing error in {xml_file.name}: {e}")
        except Exception as e:
            print(f"ERROR processing {xml_file.name}: {e}")
    
    print(f"\nConversion complete! Successfully converted {converted_count}/{len(xml_files)} files")

# Your configuration
classes = ["Longitudinal Crack", "Transverse Crack", "Alligator Crack", "Potholes"]

# Use raw strings for Windows paths to avoid escape character issues
xml_directory = r"D:\Courses\DEPI\PavementEye\data\fineTuneDataset\annotations"
output_directory = r"./yolo_annotations"

print("Starting conversion...")
print(f"XML Directory: {xml_directory}")
print(f"Output Directory: {output_directory}")
print(f"Classes: {classes}")

convert_pascalvoc_to_yolov8(xml_directory, output_directory, classes)

print("Script finished!")