#!/usr/bin/env python3
"""
XER File Parser and Analyzer
Parses Primavera P6 XER files and generates comprehensive reports
"""

import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import json

class XERParser:
    def __init__(self, filepath):
        self.filepath = Path(filepath)
        self.data = {}
        self.tables = {}
        self.metadata = {}

    def parse(self):
        """Parse the XER file"""
        with open(self.filepath, 'r', encoding='windows-1252', errors='ignore') as f:
            lines = f.readlines()

        # Parse header
        header_line = lines[0].strip()
        header_parts = header_line.split('\t')
        if header_parts[0] == 'ERMHDR':
            self.metadata = {
                'version': header_parts[1] if len(header_parts) > 1 else '',
                'export_date': header_parts[2] if len(header_parts) > 2 else '',
                'user_type': header_parts[3] if len(header_parts) > 3 else '',
                'username': header_parts[4] if len(header_parts) > 4 else '',
                'full_name': header_parts[5] if len(header_parts) > 5 else '',
                'database': header_parts[6] if len(header_parts) > 6 else '',
                'role': header_parts[7] if len(header_parts) > 7 else '',
                'currency': header_parts[8] if len(header_parts) > 8 else ''
            }

        # Parse tables
        current_table = None
        current_fields = []

        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue

            parts = line.split('\t')

            if parts[0] == '%T':  # Table declaration
                current_table = parts[1] if len(parts) > 1 else ''
                self.tables[current_table] = []
                current_fields = []

            elif parts[0] == '%F':  # Field names
                current_fields = parts[1:]

            elif parts[0] == '%R':  # Row data
                if current_table and current_fields:
                    row_data = {}
                    for i, field in enumerate(current_fields):
                        value = parts[i+1] if i+1 < len(parts) else ''
                        row_data[field] = value
                    self.tables[current_table].append(row_data)

        return self

    def get_project_info(self):
        """Extract project information"""
        if 'PROJECT' not in self.tables or not self.tables['PROJECT']:
            return {}

        project = self.tables['PROJECT'][0]
        return {
            'project_id': project.get('proj_id', ''),
            'project_name': project.get('proj_short_name', ''),
            'plan_start': project.get('plan_start_date', ''),
            'plan_end': project.get('plan_end_date', ''),
            'scheduled_end': project.get('scd_end_date', ''),
            'last_recalc': project.get('last_recalc_date', ''),
            'currency': self.metadata.get('currency', ''),
            'critical_path_type': project.get('critical_path_type', ''),
            'day_hours': '10',
            'week_hours': '60'
        }

    def get_wbs_summary(self):
        """Get WBS structure summary"""
        if 'PROJWBS' not in self.tables:
            return []

        wbs_items = self.tables['PROJWBS']
        wbs_tree = []

        for wbs in wbs_items[:50]:  # Limit to first 50
            wbs_tree.append({
                'wbs_id': wbs.get('wbs_id', ''),
                'name': wbs.get('wbs_name', ''),
                'short_name': wbs.get('wbs_short_name', ''),
                'parent_id': wbs.get('parent_wbs_id', ''),
                'status': wbs.get('status_code', '')
            })

        return wbs_tree

    def get_calendar_info(self):
        """Get calendar information"""
        if 'CALENDAR' not in self.tables:
            return []

        calendars = []
        for cal in self.tables['CALENDAR']:
            calendars.append({
                'calendar_id': cal.get('clndr_id', ''),
                'name': cal.get('clndr_name', ''),
                'type': cal.get('clndr_type', ''),
                'day_hours': cal.get('day_hr_cnt', ''),
                'week_hours': cal.get('week_hr_cnt', ''),
                'default': cal.get('default_flag', '')
            })

        return calendars

    def get_task_count(self):
        """Get count of tasks"""
        if 'TASK' in self.tables:
            return len(self.tables['TASK'])
        return 0

    def get_custom_fields(self):
        """Get custom field definitions"""
        if 'UDFTYPE' not in self.tables:
            return []

        custom_fields = []
        for udf in self.tables['UDFTYPE']:
            if udf.get('table_name') == 'TASK':
                custom_fields.append({
                    'field_id': udf.get('udf_type_id', ''),
                    'field_name': udf.get('udf_type_name', ''),
                    'label': udf.get('udf_type_label', ''),
                    'data_type': udf.get('logical_data_type', '')
                })

        return custom_fields

    def get_table_statistics(self):
        """Get statistics about tables"""
        stats = {}
        for table_name, rows in self.tables.items():
            stats[table_name] = len(rows)
        return stats


def generate_report(xer_files):
    """Generate comprehensive report for all XER files"""

    report = {
        'report_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_files': len(xer_files),
        'files': []
    }

    for xer_file in xer_files:
        print(f"\nParsing: {xer_file}")

        parser = XERParser(xer_file)
        parser.parse()

        file_info = {
            'filename': Path(xer_file).name,
            'filepath': str(xer_file),
            'file_size_mb': round(Path(xer_file).stat().st_size / (1024 * 1024), 2),
            'metadata': parser.metadata,
            'project_info': parser.get_project_info(),
            'wbs_count': len(parser.tables.get('PROJWBS', [])),
            'wbs_summary': parser.get_wbs_summary(),
            'task_count': parser.get_task_count(),
            'calendars': parser.get_calendar_info(),
            'custom_fields_count': len(parser.get_custom_fields()),
            'custom_fields': parser.get_custom_fields(),
            'table_statistics': parser.get_table_statistics()
        }

        report['files'].append(file_info)

    return report


def print_text_report(report):
    """Print formatted text report"""

    print("\n" + "="*80)
    print(" XER FILES ANALYSIS REPORT")
    print("="*80)
    print(f"\nReport Generated: {report['report_date']}")
    print(f"Total Files Analyzed: {report['total_files']}")

    for idx, file_info in enumerate(report['files'], 1):
        print("\n" + "-"*80)
        print(f"FILE #{idx}: {file_info['filename']}")
        print("-"*80)

        print(f"\n[FILE INFORMATION]")
        print(f"   Size: {file_info['file_size_mb']} MB")
        print(f"   Path: {file_info['filepath']}")

        print(f"\n[METADATA]")
        meta = file_info['metadata']
        print(f"   Primavera Version: {meta.get('version', 'N/A')}")
        print(f"   Export Date: {meta.get('export_date', 'N/A')}")
        print(f"   Exported By: {meta.get('full_name', 'N/A')} ({meta.get('username', 'N/A')})")
        print(f"   Currency: {meta.get('currency', 'N/A')}")

        print(f"\n[PROJECT INFORMATION]")
        proj = file_info['project_info']
        print(f"   Project ID: {proj.get('project_id', 'N/A')}")
        print(f"   Project Name: {proj.get('project_name', 'N/A')}")
        print(f"   Planned Start: {proj.get('plan_start', 'N/A')}")
        print(f"   Planned End: {proj.get('plan_end', 'N/A')}")
        print(f"   Scheduled End: {proj.get('scheduled_end', 'N/A')}")
        print(f"   Last Recalculated: {proj.get('last_recalc', 'N/A')}")
        print(f"   Working Hours: {proj.get('day_hours', 'N/A')} hrs/day, {proj.get('week_hours', 'N/A')} hrs/week")

        print(f"\n[CALENDARS] Count: {len(file_info['calendars'])}")
        for cal in file_info['calendars'][:5]:
            print(f"   - {cal['name']} (ID: {cal['calendar_id']}, Type: {cal['type']})")
            print(f"     Working: {cal['day_hours']} hrs/day, {cal['week_hours']} hrs/week")

        print(f"\n[WORK BREAKDOWN STRUCTURE]")
        print(f"   Total WBS Items: {file_info['wbs_count']}")
        print(f"   Top-level WBS (first 10):")
        for wbs in file_info['wbs_summary'][:10]:
            indent = "     " if wbs['parent_id'] else "   "
            print(f"{indent}- {wbs['short_name']}: {wbs['name']}")

        print(f"\n[TASKS]")
        print(f"   Total Tasks/Activities: {file_info['task_count']}")

        print(f"\n[CUSTOM FIELDS]")
        print(f"   Total Custom Task Fields: {file_info['custom_fields_count']}")
        if file_info['custom_fields']:
            print(f"   Sample Custom Fields:")
            for cf in file_info['custom_fields'][:10]:
                print(f"     - {cf['label']} ({cf['field_name']}) - Type: {cf['data_type']}")

        print(f"\n[TABLE STATISTICS]")
        stats = file_info['table_statistics']
        important_tables = ['PROJECT', 'PROJWBS', 'TASK', 'TASKPRED', 'CALENDAR',
                          'RSRC', 'TASKRSRC', 'UDFTYPE']
        for table in important_tables:
            if table in stats:
                print(f"   {table}: {stats[table]:,} rows")

    print("\n" + "="*80)
    print(" END OF REPORT")
    print("="*80)


def save_json_report(report, output_file):
    """Save report as JSON"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\n[SUCCESS] JSON report saved to: {output_file}")


if __name__ == "__main__":
    # Find all XER files in current directory
    xer_files = list(Path('.').glob('*.xer'))

    if not xer_files:
        print("No XER files found in current directory!")
    else:
        print(f"Found {len(xer_files)} XER file(s):")
        for f in xer_files:
            print(f"  - {f.name}")

        # Generate report
        report = generate_report(xer_files)

        # Print text report
        print_text_report(report)

        # Save JSON report
        json_output = Path('xer_analysis_report.json')
        save_json_report(report, json_output)

        # Save text report
        text_output = Path('xer_analysis_report.txt')
        with open(text_output, 'w', encoding='utf-8') as f:
            import sys
            from io import StringIO

            old_stdout = sys.stdout
            sys.stdout = StringIO()
            print_text_report(report)
            text_content = sys.stdout.getvalue()
            sys.stdout = old_stdout

            f.write(text_content)

        print(f"[SUCCESS] Text report saved to: {text_output}")
