# Simple script to see what happened in our workflow

def show_log():
    """Show the provenance log in a simple way."""
    try:
        with open('provenance.log', 'r') as f:
            print("=== Workflow History ===")
            for line in f:
                print(line.strip())
    except FileNotFoundError:
        print("No log file found. Run workflow.py first.")
    
    # Also show version info if available
    try:
        with open('version_info.txt', 'r') as f:
            print("\n=== Version Info ===")
            print(f.read())
    except FileNotFoundError:
        pass

if __name__ == "__main__":
    show_log()