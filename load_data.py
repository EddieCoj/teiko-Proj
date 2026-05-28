import sqlite3
import pandas as pd

def load_csv_to_sqlite(csv_path='cell-count.csv', db_path='teiko.db'):
    # Read the CSV
    df = pd.read_csv(csv_path)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Drop tables if they exist
    cursor.execute("DROP TABLE IF EXISTS cell_counts;")
    cursor.execute("DROP TABLE IF EXISTS samples;")
    cursor.execute("DROP TABLE IF EXISTS subjects;")
    
    # Create subjects table
    cursor.execute("""
        CREATE TABLE subjects(
            subject_id TEXT PRIMARY KEY,
            age INTEGER,
            sex TEXT,
            condition TEXT
        );
    """)
    
    # Create samples table
    cursor.execute("""
        CREATE TABLE samples(
            sample_id TEXT PRIMARY KEY,
            subject_id TEXT,
            project TEXT,
            sample_type TEXT,
            treatment TEXT,
            response TEXT,
            time_from_treatment_start INTEGER,
            FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
        );
    """)
    
    # Create cell_counts table with composite key
    cursor.execute("""
        CREATE TABLE cell_counts(
            sample_id TEXT,
            population TEXT,
            count INTEGER,
            PRIMARY KEY (sample_id, population),
            FOREIGN KEY (sample_id) REFERENCES samples(sample_id)
        );
    """)
    
    # Insert subjects (unique)
    subjects_df = df[['subject', 'age', 'sex', 'condition']].drop_duplicates('subject')
    subjects_df = subjects_df.rename(columns={'subject': 'subject_id'})
    subjects_df.to_sql('subjects', conn, if_exists='append', index=False)
    
    # Insert samples
    samples_df = df[['sample', 'subject', 'project', 'sample_type', 
                     'treatment', 'response', 'time_from_treatment_start']].copy()
    samples_df = samples_df.rename(columns={'sample': 'sample_id', 'subject': 'subject_id'})
    samples_df.to_sql('samples', conn, if_exists='append', index=False)
    
    # Insert cell_counts (melt)
    id_vars = ['sample']
    value_vars = ['b_cell', 'cd8_t_cell', 'cd4_t_cell', 'nk_cell', 'monocyte']
    cell_counts_df = pd.melt(df, id_vars=id_vars, value_vars=value_vars, 
                              var_name='population', value_name='count')
    cell_counts_df = cell_counts_df.rename(columns={'sample': 'sample_id'})
    cell_counts_df.to_sql('cell_counts', conn, if_exists='append', index=False)
    
    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_samples_project ON samples(project);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_samples_response ON samples(response);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cell_counts_sample ON cell_counts(sample_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cell_counts_population ON cell_counts(population);")
    
    conn.commit()
    conn.close()
    
    print(f"Database created successfully with {len(subjects_df)} subjects, {len(samples_df)} samples")

if __name__ == "__main__":
    load_csv_to_sqlite()
