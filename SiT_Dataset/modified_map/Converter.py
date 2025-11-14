import json
import xml.etree.ElementTree as ET
from xml.dom import minidom

def calculate_bounding_box(coords):
    x_coords = [p[0] for p in coords]
    y_coords = [p[1] for p in coords]
    min_x, max_x = min(x_coords), max(x_coords)
    min_y, max_y = min(y_coords), max(y_coords)
    return max_x - min_x, max_y - min_y

def json_to_sdf(json_path, output_path):
    with open(json_path) as f:
        data = json.load(f)

    sdf = ET.Element('sdf', version='1.6')
    model = ET.SubElement(sdf, 'model', name='auto_generated_model')

    # Building만 반영
    height_config = {
        'Building': 3.0
    }
    color_config = {
        'Building': '0.3 0.3 0.3 1'
    }
    allowed_categories = ['Building']

    for category, objects in data.items():
        if category not in allowed_categories or not objects:
            continue
        for idx, obj_coords in enumerate(objects):
            if not isinstance(obj_coords, list) or len(obj_coords) < 4:
                continue
            model_name = f"{category}_{idx+1}"
            submodel = ET.SubElement(model, 'model', name=model_name)
            ET.SubElement(submodel, 'static').text = 'true'
            link = ET.SubElement(submodel, 'link', name=f'{model_name}_link')
            current_height = height_config['Building']

            for element_type in ['collision', 'visual']:
                elem = ET.SubElement(link, element_type, name=f'{element_type}_mesh')
                origin = ET.SubElement(elem, 'origin')
                origin.set('xyz', f"0 0 0")
                geometry = ET.SubElement(elem, 'geometry')

                # Building은 polyline
                polyline = ET.SubElement(geometry, 'polyline')
                for point in obj_coords:
                    if isinstance(point, list) and len(point) == 2:
                        x, y = point
                        ET.SubElement(polyline, 'point').text = f"{x} {y}"
                ET.SubElement(polyline, 'height').text = str(current_height)

                if element_type == 'visual':
                    material = ET.SubElement(elem, 'material')
                    diffuse = ET.SubElement(material, 'diffuse')
                    diffuse.text = color_config['Building']

    # XML 포맷팅
    rough_xml = ET.tostring(sdf, 'utf-8')
    parsed = minidom.parseString(rough_xml)
    pretty_xml = parsed.toprettyxml(indent=" ", encoding='utf-8').decode('utf-8')
    pretty_xml = '\n'.join([line for line in pretty_xml.split('\n') if line.strip()])

    with open(output_path, 'w') as f:
        f.write(pretty_xml)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', required=True, help='Input JSON file')
    parser.add_argument('-o', '--output', default='output.sdf', help='Output SDF file')
    args = parser.parse_args()
    json_to_sdf(args.input, args.output)
