# config/thresholds.py

# In-memory dictionary to store user thresholds
# (In real-world use Redis or DB)
user_thresholds = {}

def set_threshold(user_id, threshold):
    user_thresholds[user_id] = threshold

def get_threshold(user_id):
    return user_thresholds.get(user_id)
