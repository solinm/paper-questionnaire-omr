import sqlite3
import json
import argparse
import os
import csv

def main():
    parser = argparse.ArgumentParser(description="Extract survey responses from an SDAPS survey.sqlite database.")
    parser.add_argument("directory", help="The directory containing the survey.sqlite file (e.g., projects/gds-en/).")
    parser.add_argument("--output", "-o", default=None, help="Output file path for the CSV (default: <directory>/survey_results.csv)")
    
    args = parser.parse_args()
    
    output_path = args.output if args.output else os.path.join(args.directory, "survey_results.csv")

    db_path = os.path.join(args.directory, 'survey.sqlite')
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
    except Exception as e:
        print(f"Failed to connect to the database: {e}")
        return

    surveys_row = conn.execute('SELECT json FROM surveys LIMIT 1').fetchone()
    if not surveys_row:
        print("Error: No survey schema found in the 'surveys' table.")
        return

    survey_schema = json.loads(surveys_row[0])
    questionnaire = survey_schema.get('questionnaire', {})
    qobjects = questionnaire.get('qobjects', [])

    question_map = {}
    boxes_map = {}

    for q in qobjects:
        q_id = "^".join(map(str, q.get('id', [])))
        if 'question' in q:
            question_map[q_id] = q['question']
        
        for box in q.get('boxes', []):
            box_id = "^".join(map(str, box.get('id', [])))
            boxes_map[box_id] = {
                'q_id': q_id,
                'question': q.get('question', ''),
                'text': box.get('text', ''),
                'value': box.get('value', ''),
                'type': box.get('_class', '')
            }

    sheets_rows = conn.execute('SELECT json FROM sheets').fetchall()
    all_responses = []

    for i, row in enumerate(sheets_rows):
        sheet_data = json.loads(row[0])
        data = sheet_data.get('data', {})
        
        answers_by_q = {q_text: [] for q_text in question_map.values() if q_text}
        
        for box_id, box_state in data.items():
            if box_id not in boxes_map:
                continue
                
            box_info = boxes_map[box_id]
            q_text = box_info['question']
            b_text = box_info['text']
            b_val = box_info['value']
            
            box_type = box_state.get('_class', '')
            is_checked = box_state.get('state', False)
                
            if not q_text:
                continue
                
            if box_type == 'Textbox':
                val = box_state.get('text', '')
                if val:
                    answers_by_q[q_text].append(val)
            elif box_type == 'Checkbox':
                if is_checked:
                    ans_str = b_text if b_text else str(b_val)
                    answers_by_q[q_text].append(ans_str)
                    
        row_dict = {"Survey_Number": i + 1}
        for q_id, q_text in question_map.items():
            if q_text:
                ans_list = answers_by_q.get(q_text, [])
                row_dict[q_text] = ", ".join(ans_list) if ans_list else "None/Not Answered"
                
        all_responses.append(row_dict)

    if not all_responses:
        print("No survey responses found the sheets table.")
        return

    fieldnames = ["Survey_Number"]
    for q_text in question_map.values():
        if q_text and q_text not in fieldnames:
            fieldnames.append(q_text)
            
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for response in all_responses:
            writer.writerow(response)
            
    print(f"Successfully extracted {len(all_responses)} survey responses to '{output_path}'")


if __name__ == "__main__":
    main()
