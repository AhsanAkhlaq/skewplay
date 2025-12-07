import os

def get_user_storage_usage(user_id: str) -> int:
    """
    Calculates the total bytes used by a user in the storage directory.
    Path: storage/{user_id}
    """
    storage_root = "storage"
    user_dir = os.path.join(storage_root, user_id)
    
    total_size = 0
    
    if not os.path.exists(user_dir):
        return 0
        
    for dirpath, dirnames, filenames in os.walk(user_dir):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
                
    return total_size
