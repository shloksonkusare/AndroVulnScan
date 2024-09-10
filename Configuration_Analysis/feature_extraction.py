import xml.etree.ElementTree as ET
import re

def parse_manifest(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    permissions = [elem.attrib['{http://schemas.android.com/apk/res/android}name'].split('.')[-1] 
                   for elem in root.findall('uses-permission')]
    
    components = {
        'activities': len(root.findall('application/activity')),
        'services': len(root.findall('application/service')),
        'receivers': len(root.findall('application/receiver')),
        'providers': len(root.findall('application/provider')),
    }
    
    min_sdk = root.find('uses-sdk').attrib.get('{http://schemas.android.com/apk/res/android}minSdkVersion', 'Unknown')
    
    return {
        'permissions': permissions,
        'components': components,
        'min_sdk': min_sdk
    }

def parse_gradle(file_path):
    dependencies = []
    with open(file_path, 'r') as file:
        for line in file:
            match = re.search(r'implementation\s+["\']([^"\']+)["\']', line)
            if match:
                dependencies.append(match.group(1).split(':')[1])
    
    return {'dependencies': dependencies}
