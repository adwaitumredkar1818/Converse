import os

def inspect_dataset(base_path: str = "data/raw"):
    print("=" * 60)
    print(f"📊 DATASET INSPECTION: {base_path}")
    print("=" * 60)

    if not os.path.exists(base_path):
        print(f"❌ Path {base_path} does not exist.")
        return

    total_files = 0
    total_size_bytes = 0
    file_summary = {}

    for root, dirs, files in os.walk(base_path):
        if not files:
            continue

        print(f"\n📂 Directory: {root}")
        print(f"   Files count: {len(files)}")

        for file in files:
            if file.startswith("."):
                continue  # skip hidden files like .DS_Store
            file_path = os.path.join(root, file)
            size = os.path.getsize(file_path)
            ext = os.path.splitext(file)[1].lower() or "no_extension"

            total_files += 1
            total_size_bytes += size

            if ext not in file_summary:
                file_summary[ext] = {"count": 0, "size_bytes": 0}
            file_summary[ext]["count"] += 1
            file_summary[ext]["size_bytes"] += size

            size_mb = size / (1024 * 1024)
            print(f"   - {file} ({size_mb:.2f} MB)")

    print("\n" + "=" * 60)
    print("📈 SUMMARY BY FILE TYPE")
    print("=" * 60)
    for ext, info in file_summary.items():
        mb = info["size_bytes"] / (1024 * 1024)
        print(f"  • {ext.upper()}: {info['count']} file(s), Total Size: {mb:.2f} MB")

    total_mb = total_size_bytes / (1024 * 1024)
    print(f"\n📁 Total Files: {total_files}")
    print(f"💾 Total Size: {total_mb:.2f} MB")
    print("=" * 60)

if __name__ == "__main__":
    inspect_dataset()