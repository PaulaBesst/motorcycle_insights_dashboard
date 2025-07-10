# generate_dummy_data.py
import pandas as pd
import numpy as np
from datetime import timedelta

def create_dummy_data():
    np.random.seed(42)
    dates = pd.date_range(start='2024-01-01 07:00:00', periods=168, freq='1H')
    
    data = []
    for i, date in enumerate(dates):
        hour = date.hour
        base_compliance = 0.6 + 0.3 * np.sin((hour - 6) * np.pi / 12)
        noise = np.random.normal(0, 0.15)
        compliance_rate = max(0.1, min(0.95, base_compliance + noise))

        total_detections = np.random.poisson(12) + 5
        helmet_compliance = int(total_detections * compliance_rate)
        child_passengers = np.random.poisson(1.5) if np.random.random() < 0.4 else 0

        mirror_probs = np.random.dirichlet([2, 3, 4])
        mirror_counts = np.random.multinomial(total_detections, mirror_probs)
        no_mirror = mirror_counts[0]
        left_mirror = mirror_counts[1]
        right_mirror = mirror_counts[2]
        both_mirrors = mirror_counts[1] + mirror_counts[2]

        data.append({
            'timestamp': date,
            'helmet_compliance': helmet_compliance,
            'total_detections': total_detections,
            'child_passengers': child_passengers,
            'no_mirror': no_mirror,
            'left_mirror': left_mirror,
            'right_mirror': right_mirror,
            'both_mirrors': both_mirrors,
            'time_window': f"{date.strftime('%H:%M')}-{(date + timedelta(hours=1)).strftime('%H:%M')}",
            'hour': hour,
            'day_of_week': date.strftime('%A')
        })
    
    return pd.DataFrame(data)

if __name__ == "__main__":
    df = create_dummy_data()
    df.to_csv("dashboard/data.csv", index=False)  # Save to file (adjust path if needed)
