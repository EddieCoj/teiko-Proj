import sqlite3
import pandas as pd
import numpy as np
from scipy.stats import mannwhitneyu
from scipy.stats import norm

def part2_relative_frequencies(db_path='teiko.db'):
    """Part 2: Calculate relative frequencies for each cell population"""
    conn = sqlite3.connect(db_path)

    query = """
        SELECT
            sample_id, 
            SUM(count) OVER (PARTITION BY sample_id) as total_count,
            population, 
            count,
            100.0 * count / SUM(count) OVER (PARTITION BY sample_id) AS percentage
        FROM cell_counts
        ORDER BY sample_id, population
    """

    result = pd.read_sql_query(query, conn)
    conn.close()

    result['percentage'] = result['percentage'].round(2)

    # Save to CSV for reproducibility
    result.to_csv('part2_frequencies.csv', index=False)
    print(f"Part 2 complete: {len(result)} rows saved to part2_frequencies.csv")

    return result


def part3_statistical_test(db_path='teiko.db'):
    """Part 3: Statistical comparison of responders vs non-responders (PBMC only)"""
    conn = sqlite3.connect(db_path)

    # Query with PBMC filter - FIXED syntax
    query = """
        SELECT
            c.population,
            s.sample_id,
            s.response,
            100.0 * c.count / SUM(c.count) OVER (PARTITION BY s.sample_id) AS percentage
        FROM samples s
        INNER JOIN cell_counts c ON s.sample_id = c.sample_id
        INNER JOIN subjects sub ON s.subject_id = sub.subject_id
        WHERE sub.condition = 'melanoma'
            AND s.treatment = 'miraclib'
            AND s.response IS NOT NULL
            AND s.sample_type = 'PBMC'
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    populations = df['population'].unique()
    results = []

    print("=" * 70)
    print("PART 3: Responders vs Non-Responders (PBMC samples only)")
    print("=" * 70)

    for pop in populations:
        # FIXED: Removed brackets and fixed syntax
        responders = df[(df['population'] == pop) & (df['response'] == 'yes')]['percentage']
        non_responders = df[(df['population'] == pop) & (df['response'] == 'no')]['percentage']

        n_responders = len(responders)
        n_nonresponders = len(non_responders)

        stat, p_value = mannwhitneyu(responders, non_responders, alternative='two-sided')
        
        median_resp = responders.median()
        median_nonresp = non_responders.median()

        # Effect size calculation
        z_score = norm.ppf(p_value / 2)
        n_total = n_responders + n_nonresponders
        effect_size = abs(z_score) / np.sqrt(n_total) if n_total > 0 else 0

        results.append({
            'Population': pop,
            'N_Responders': n_responders,
            'N_NonResponders': n_nonresponders,
            'Median_Responders_%': round(median_resp, 2),
            'Median_NonResponders_%': round(median_nonresp, 2),
            'P_value': p_value,
            'Effect_Size': round(effect_size, 3),
            'Significant': p_value < 0.05
        })

        status = "✅ SIGNIFICANT" if p_value < 0.05 else "❌ Not significant"
        print(f"\n{pop}:")
        print(f"  p = {p_value:.4f} ({status})")
        print(f"  Medians: {median_resp:.1f}% (responders) vs {median_nonresp:.1f}% (non-responders)")
        print(f"  Effect size (r) = {effect_size:.3f}")

    results_df = pd.DataFrame(results)
    results_df.to_csv('part3_statistics.csv', index=False)
    print(f"\n✓ Part 3 complete: Results saved to part3_statistics.csv")

    return results_df


def part4_subset_analysis(db_path='teiko.db'):
    """
    Part 4: Analyze baseline melanoma PBMC samples treated with miraclib
    Returns: project_counts, response_counts, sex_counts, avg_b_cells
    """
    conn = sqlite3.connect(db_path)
    
    # Query with proper filters (PBMC only, baseline)
    queryJoined = """
        SELECT
            c.population,
            c.count,
            s.sample_id,
            s.response,
            s.subject_id,
            s.sample_type,
            s.treatment,
            s.project,
            sub.condition,
            sub.sex,
            s.time_from_treatment_start
        FROM samples s
        JOIN cell_counts c 
            ON s.sample_id = c.sample_id
        JOIN subjects sub 
            ON s.subject_id = sub.subject_id
        WHERE condition = 'melanoma'
            AND treatment = 'miraclib'
            AND sample_type = 'PBMC'
            AND time_from_treatment_start = 0
            AND response IS NOT NULL
    """
    joinedDF2 = pd.read_sql_query(queryJoined, conn)
    conn.close()

    print("=" * 60)
    print("PART 4: BASELINE MELANOMA ANALYSIS (time=0, miraclib, PBMC)")
    print("=" * 60)
    
    # 1. How many samples from each project
    print("\n📊 Samples per project:")
    project_counts = joinedDF2[['sample_id', 'project']].drop_duplicates()['project'].value_counts()
    print(project_counts)
    
    # 2. How many subjects were responders/non-responders
    print("\n📊 Response status (unique subjects):")
    response_counts = joinedDF2[['subject_id', 'response']].drop_duplicates()['response'].value_counts()
    print(f"  Responders (yes): {response_counts.get('yes', 0)}")
    print(f"  Non-responders (no): {response_counts.get('no', 0)}")
    
    # 3. How many subjects were males/females
    print("\n📊 Gender distribution (unique subjects):")
    sex_counts = joinedDF2[['subject_id', 'sex']].drop_duplicates()['sex'].value_counts()
    print(f"  Male: {sex_counts.get('M', 0)}")
    print(f"  Female: {sex_counts.get('F', 0)}")
    
    # 4. Average number of B Cells for Melanoma Males Who Responded at Baseline
    print("\n📊 Average B cells for male responders at baseline:")
    avg_b_cells = joinedDF2['count'][
        (joinedDF2['sex'] == 'M') & 
        (joinedDF2['response'] == 'yes') & 
        (joinedDF2['population'] == 'b_cell')
    ].mean()
    
    print(f"  Average B cell count: {avg_b_cells:.2f}")
    
    # Save results to text file for pipeline
    with open('part4_results.txt', 'w') as f:
        f.write("PART 4: BASELINE MELANOMA ANALYSIS\n")
        f.write("=" * 40 + "\n")
        f.write(f"Samples per project:\n{project_counts.to_string()}\n\n")
        f.write(f"Responders: {response_counts.get('yes', 0)}\n")
        f.write(f"Non-responders: {response_counts.get('no', 0)}\n\n")
        f.write(f"Males: {sex_counts.get('M', 0)}\n")
        f.write(f"Females: {sex_counts.get('F', 0)}\n\n")
        f.write(f"Average B cells for male responders: {avg_b_cells:.2f}\n")
    
    print(f"\n✓ Part 4 complete: Results saved to part4_results.txt")
    
    return project_counts, response_counts, sex_counts, avg_b_cells


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("RUNNING COMPLETE ANALYSIS PIPELINE")
    print("=" * 70)
    
    # Test Part 2
    print("\n" + "=" * 70)
    print("PART 2: Relative Frequencies")
    print("=" * 70)
    result2 = part2_relative_frequencies('teiko.db')
    print(f"\n✓ Part 2 complete: {len(result2)} rows")
    
    # Test Part 3
    print("\n" + "=" * 70)
    print("PART 3: Statistical Analysis")
    print("=" * 70)
    result3 = part3_statistical_test('teiko.db')
    print(f"\n✓ Part 3 complete: Statistics saved")
    
    # Test Part 4
    print("\n" + "=" * 70)
    print("PART 4: Subset Analysis")
    print("=" * 70)
    proj_counts, resp_counts, sex_counts, avg_b = part4_subset_analysis('teiko.db')
    print(f"\n✓ Part 4 complete: Results saved")
    
    print("\n" + "=" * 70)
    print("ALL TESTS COMPLETED SUCCESSFULLY")
    print("=" * 70)