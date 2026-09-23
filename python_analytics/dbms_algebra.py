import pandas as pd

def link_complaints_to_infrastructure(subscribers_path, complaints_path):
    """
    Executes relational algebra JOIN operation (DBMS Unit 2):
    Complaints ⋈ Subscribers ⋈ Towers
    """
    df_sub = pd.read_csv(subscribers_path)
    df_cmp = pd.read_csv(complaints_path)
    
    # Natural Join on subscriber_id
    linked_data = pd.merge(df_cmp, df_sub, on="subscriber_id", suffixes=('_complaint', '_subscriber'))
    return linked_data