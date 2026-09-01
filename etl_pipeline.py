import re
import pandas as pd
import numpy as np
from typing import Tuple, Dict, List

class CollegeDataETL:
    BRANCH_MAPPINGS = {
        'COMP SCI': 'CSE',
        'COMPUTER SCIENCE': 'CSE',
        'CS': 'CSE',
        'CSE': 'CSE',
        'INFORMATION TECHNOLOGY': 'IT',
        'INFORMATION TECH': 'IT',
        'INFO TECH': 'IT',
        'IT': 'IT',
        'ELECTRONICS': 'ECE',
        'ELECTRONICS AND COMMUNICATION': 'ECE',
        'ECE': 'ECE',
        'MECHANICAL': 'MECH',
        'MECH ENGG': 'MECH',
        'MECH': 'MECH',
        'CIVIL': 'CIVIL',
        'CIVIL ENGG': 'CIVIL',
        'ELECTRICAL': 'EEE',
        'ELECTRICAL & ELECTRONICS': 'EEE',
        'ELECTRICAL AND ELECTRONICS': 'EEE',
        'EEE': 'EEE'
    }

    def __init__(self):
        self.audit_errors: List[Dict] = []

    def _log_error(self, source: str, student_id: str, issue: str, raw_data: dict):
        self.audit_errors.append({
            "source_file": source,
            "student_id": student_id if pd.notna(student_id) else "MISSING",
            "issue": issue,
            "raw_record": str(raw_data)
        })

    def clean_student_master(self, df_raw: pd.DataFrame) -> pd.DataFrame:
        df = df_raw.copy()
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

        if 'student_id' not in df.columns:
            raise ValueError("Student Master file missing 'student_id' column")

        # 1. Quarantine missing IDs
        invalid_ids = df[df['student_id'].isna()]
        for _, row in invalid_ids.iterrows():
            self._log_error("student_master", None, "Missing student_id", row.to_dict())
        df = df.dropna(subset=['student_id'])

        # 2. Standardize ID format
        df['student_id'] = df['student_id'].astype(str).str.strip().str.upper()

        # 3. Clean Student Names
        if 'name' in df.columns:
            df['name'] = (
                df['name']
                .astype(str)
                .str.replace(r'^(mr\.|ms\.|dr\.|mrs\.)\s+', '', flags=re.IGNORECASE, regex=True)
                .str.strip()
                .str.title()
            )

        # 4. Standardize Branch Aliases
        if 'branch' in df.columns:
            df['branch'] = df['branch'].astype(str).str.strip().str.upper()
            df['branch'] = df['branch'].replace(self.BRANCH_MAPPINGS)

        # 5. Deduplicate
        df = df.drop_duplicates(subset=['student_id'], keep='first')
        return df

    def clean_academic_records(self, df_raw: pd.DataFrame) -> pd.DataFrame:
        df = df_raw.copy()
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

        if 'student_id' not in df.columns:
            raise ValueError("Academics file missing 'student_id' column")

        df = df.dropna(subset=['student_id'])
        df['student_id'] = df['student_id'].astype(str).str.strip().str.upper()

        # Clean SGPA
        if 'sgpa' in df.columns:
            df['sgpa'] = pd.to_numeric(df['sgpa'], errors='coerce')
            invalid_sgpa = df[(df['sgpa'].isna()) | (df['sgpa'] < 0.0) | (df['sgpa'] > 10.0)]
            for _, row in invalid_sgpa.iterrows():
                self._log_error("academics", row.get('student_id'), "Invalid SGPA out of range [0.0 - 10.0]", row.to_dict())
            df['sgpa'] = df['sgpa'].clip(lower=0.0, upper=10.0).fillna(0.0)
        else:
            df['sgpa'] = 0.0

        # Clean CGPA
        if 'cgpa' in df.columns:
            df['cgpa'] = pd.to_numeric(df['cgpa'], errors='coerce')
            invalid_cgpa = df[(df['cgpa'].isna()) | (df['cgpa'] < 0.0) | (df['cgpa'] > 10.0)]
            for _, row in invalid_cgpa.iterrows():
                self._log_error("academics", row.get('student_id'), "Invalid CGPA out of range [0.0 - 10.0]", row.to_dict())
            df['cgpa'] = df['cgpa'].clip(lower=0.0, upper=10.0).fillna(0.0)
        else:
            df['cgpa'] = 0.0

        # Clean Backlogs
        if 'backlogs' in df.columns:
            df['backlogs'] = pd.to_numeric(df['backlogs'], errors='coerce').fillna(0).astype(int)
            neg_backlogs = df['backlogs'] < 0
            for _, row in df[neg_backlogs].iterrows():
                self._log_error("academics", row.get('student_id'), "Negative backlogs count", row.to_dict())
            df['backlogs'] = df['backlogs'].clip(lower=0)
        else:
            df['backlogs'] = 0

        # Deduplicate
        df = df.sort_values(by='cgpa', ascending=False).drop_duplicates(subset=['student_id'], keep='first')
        return df

    def clean_attendance_records(self, df_raw: pd.DataFrame) -> pd.DataFrame:
        df = df_raw.copy()
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

        if 'student_id' not in df.columns:
            raise ValueError("Attendance file missing 'student_id' column")

        df = df.dropna(subset=['student_id'])
        df['student_id'] = df['student_id'].astype(str).str.strip().str.upper()

        # Clean Total Classes
        if 'total_classes' in df.columns:
            df['total_classes'] = pd.to_numeric(df['total_classes'], errors='coerce').fillna(0).astype(int)
            neg_total = df['total_classes'] < 0
            for _, row in df[neg_total].iterrows():
                self._log_error("attendance", row.get('student_id'), "Negative total classes", row.to_dict())
            df['total_classes'] = df['total_classes'].clip(lower=0)
        else:
            df['total_classes'] = 0

        # Clean Attended Classes
        if 'attended_classes' in df.columns:
            df['attended_classes'] = pd.to_numeric(df['attended_classes'], errors='coerce').fillna(0).astype(int)
            neg_attended = df['attended_classes'] < 0
            for _, row in df[neg_attended].iterrows():
                self._log_error("attendance", row.get('student_id'), "Negative attended classes", row.to_dict())
            df['attended_classes'] = df['attended_classes'].clip(lower=0)
        else:
            df['attended_classes'] = 0

        # Validate attended <= total
        invalid_mask = df['attended_classes'] > df['total_classes']
        for _, row in df[invalid_mask].iterrows():
            self._log_error("attendance", row.get('student_id'), "Attended classes exceeds total classes", row.to_dict())
        df.loc[invalid_mask, 'attended_classes'] = df.loc[invalid_mask, 'total_classes']

        # Calculate percentage
        df['attendance_pct'] = np.where(
            df['total_classes'] > 0,
            (df['attended_classes'] / df['total_classes']) * 100.0,
            0.0
        )
        df['attendance_pct'] = df['attendance_pct'].round(2)

        df = df.drop_duplicates(subset=['student_id'], keep='first')
        return df

    def clean_placement_records(self, df_raw: pd.DataFrame) -> pd.DataFrame:
        df = df_raw.copy()
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

        if 'student_id' not in df.columns:
            raise ValueError("Placement file missing 'student_id' column")

        df = df.dropna(subset=['student_id'])
        df['student_id'] = df['student_id'].astype(str).str.strip().str.upper()

        # Registration status
        if 'is_registered' in df.columns:
            df['is_registered'] = df['is_registered'].astype(str).str.strip().str.lower()
            df['is_registered'] = df['is_registered'].isin(['true', '1', 'yes', 'y'])
        else:
            df['is_registered'] = False

        # Clean package LPA
        if 'package_lpa' in df.columns:
            df['package_lpa'] = pd.to_numeric(df['package_lpa'], errors='coerce').fillna(0.0)
            neg_package = df['package_lpa'] < 0
            for _, row in df[neg_package].iterrows():
                self._log_error("placement", row.get('student_id'), "Negative package LPA", row.to_dict())
            df['package_lpa'] = df['package_lpa'].clip(lower=0.0)
        else:
            df['package_lpa'] = 0.0

        # Clean offers count
        if 'offers_count' in df.columns:
            df['offers_count'] = pd.to_numeric(df['offers_count'], errors='coerce').fillna(0).astype(int)
            neg_offers = df['offers_count'] < 0
            for _, row in df[neg_offers].iterrows():
                self._log_error("placement", row.get('student_id'), "Negative offers count", row.to_dict())
            df['offers_count'] = df['offers_count'].clip(lower=0)
        else:
            df['offers_count'] = 0

        # Clean placement status text
        if 'status' in df.columns:
            df['status'] = df['status'].astype(str).str.strip().str.upper()
        else:
            df['status'] = 'UNPLACED'

        df = df.drop_duplicates(subset=['student_id'], keep='first')
        return df

    def integrate_all(
        self, 
        df_students: pd.DataFrame, 
        df_academics: pd.DataFrame, 
        df_attendance: pd.DataFrame, 
        df_placement: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        # 1. Clean individual sources
        c_students = self.clean_student_master(df_students)
        c_academics = self.clean_academic_records(df_academics)
        c_attendance = self.clean_attendance_records(df_attendance)
        c_placement = self.clean_placement_records(df_placement)

        # 2. Merge on unique student_id
        merged = c_students.merge(c_academics, on='student_id', how='left')
        merged = merged.merge(c_attendance, on='student_id', how='left')
        merged = merged.merge(c_placement, on='student_id', how='left')

        # 3. Fill default values for missing records
        merged['cgpa'] = merged['cgpa'].fillna(0.0)
        merged['backlogs'] = merged['backlogs'].fillna(0).astype(int)
        merged['attendance_pct'] = merged['attendance_pct'].fillna(0.0)
        merged['is_registered'] = merged['is_registered'].fillna(False)
        merged['offers_count'] = merged['offers_count'].fillna(0).astype(int)
        merged['package_lpa'] = merged['package_lpa'].fillna(0.0)
        merged['status'] = merged['status'].fillna('UNPLACED')

        # 4. Derive Academic Standing & Risk Indicator
        conditions = [
            (merged['attendance_pct'] < 75.0) & (merged['cgpa'] < 6.0),
            (merged['attendance_pct'] < 75.0),
            (merged['cgpa'] < 6.0) | (merged['backlogs'] > 0)
        ]
        choices = ['CRITICAL_RISK', 'ATTENDANCE_SHORTAGE', 'ACADEMIC_DEFICIT']
        merged['academic_standing'] = np.select(conditions, choices, default='GOOD_STANDING')

        # 5. Derive Placement Eligibility
        merged['is_placement_eligible'] = (
            (merged['cgpa'] >= 6.5) &
            (merged['attendance_pct'] >= 75.0) &
            (merged['backlogs'] == 0) &
            (merged['is_registered'] == True)
        )

        df_audit = pd.DataFrame(self.audit_errors)
        return merged, df_audit